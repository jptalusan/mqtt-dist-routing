import json
import threading
import time
import src.query_generator as generator
import common.src.basic_utils as utils
from common.src.mqtt_utils import MyMQTTClass
from common.conf import GLOBAL_VARS
from pprint import pprint
import random

class Broker_Mqtt(MyMQTTClass):
    def __init__(self, client_id=None, host="localhost", port=1883, keep_alive=60, clean_session=True, mongodb_c=None):
        super().__init__(client_id, host, port, keep_alive, clean_session)
        print("init broker mqtt")
        self._mongodb_c = mongodb_c

        self._timer_task = threading.Thread(target=self.get_unsent_tasks, args = ())
        self._timer_task.start()

        self._collect_tasks = threading.Thread(target=self.compile_tasks_by_id, args = ())
        self._collect_tasks.start()

    def mqtt_on_message(self, mqttc, obj, msg):
        # print("Inheritance:" + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        self.parse_topic(msg)

    def start_unsent_tasks_thread(self):
        if not self._timer_task.is_alive():
            print("Started get_unsent_task thread.")
            self._timer_task = threading.Thread(target=self.get_unsent_tasks, args = ())
            self._timer_task.start()
        else:
            print("get_unsent_task thread already running.")

    def parse_topic(self, msg):
        t_arr = msg.topic.split("/")
        print(msg.topic)

        if msg.topic == GLOBAL_VARS.SIMULATED_QUERY_TO_BROKER:
            data = json.loads(utils.decode(msg.payload))
            print("Broker receives : {}".format(data))

            tasks = generator.get_tasks(self._mongodb_c, data['x'], data['y'], data['number_of_queries'], sorted=True)
            # pprint(tasks)
            self.generate_mongo_tasks_entry(tasks)
            self.start_unsent_tasks_thread()

        if msg.topic == GLOBAL_VARS.QUERY_TO_BROKER:
                print("Broker receives : {}".format(str(msg.payload)))
                self.generate_mongo_payload(msg.payload)
                self.start_unsent_tasks_thread()

        if GLOBAL_VARS.RESPONSE_TO_BROKER in msg.topic:
            rsu = t_arr[-1]
            print("RSU:", rsu)
            # Check if the name is RSU-XXXX
            # if DEBUG:
            # if 'rsu' in rsu: 
            if rsu in list(GLOBAL_VARS.RSUS.values()):
                # update mongodb entry as Responded (2)
                data = json.loads(utils.decode(msg.payload))

                route = data['route']
                utils.print_log("worker-{} responded with :{}".format(rsu, data['_id']))
                self._mongodb_c.update_one("tasks", data['_id'], {"state": GLOBAL_VARS.TASK_STATES["RESPONDED"],
                                                              "processed_time": utils.time_print(int),
                                                              "route": route,
                                                              "next_node": route[-1]})
                utils.print_log("Updated: {}".format(data['_id']))

                pass
        
        if "middlleware" in t_arr and "processed" in t_arr:
            rsu = t_arr[-1]
            # Check if the name is RSU-XXXX
            if 'rsu' in rsu.lower():
                # update mongodb entry as Responded (2)
                pass

        pass

    def generate_mongo_tasks_entry(self, tasks):
        for task in tasks:
            data = task.get_json()
            data['inquiry_time'] = utils.time_print(int)
            data['processed_time'] = None
            data['state'] = GLOBAL_VARS.TASK_STATES["UNSENT"]
            data['next_node'] = None
            data['route'] = None
            t_id = data['_id']

            # print("Finding:", t_id)
            _DB = self._mongodb_c.get_db("admin")
            found = _DB["tasks"].count_documents({"_id": t_id})
            if found == 0:
                t_id = self._mongodb_c.insert("tasks", data)
                # print("\tinserted: {}".format(t_id))
            else:
                # print("\tID already exists")
                pass

    # Unsent = 0, Sent = 1, Responded = 2, Task_done = 3
    def generate_mongo_payload(self, message):
        print("generate_mongo_payload:", len(message))
        _m = utils.decode(message)
        _d = json.loads(_m)
        data = _d['data']
        data['inquiry_time'] = utils.time_print(int)
        data['processed_time'] = None
        data['state'] = GLOBAL_VARS.TASK_STATES["UNSENT"]
        data['next_node'] = None
        data['route'] = None
        t_id = data['_id']

        # print("Finding:", t_id)
        _DB = self._mongodb_c.get_db("admin")
        found = _DB["tasks"].count_documents({"_id": t_id})
        if found == 0:
            t_id = self._mongodb_c.insert("tasks", data)
            # print("\tinserted: {}".format(t_id))
        else:
            # print("\tID already exists")
            pass

    # TODO: If a subtask in the middle of a task is ERROR:99, change all the tasks to ERROR as well.
    # But if its the last of the subtask then its ok i guess.
    def check_errors(self):
        pass
    
    # maybe better to keep sending tasks until there is a response.
    # maybe change to while loop
    # Some issue here of not getting anything looping when no message arrives.

    # TODO: Check or create a new mqtt topic for replying to broker's inquiry of how "loaded" the RSUs are (task queue length) as well as checking distance between optimal
    # What is the optimal grid? rsu below in line 120?
    def get_unsent_tasks(self):
        print("get_unsent_tasks()")
        tasks = list(self._mongodb_c.find("tasks", {"state": {"$lt": GLOBAL_VARS.TASK_STATES["PROCESSED"]}}))

        while len(tasks) > 0:
            for task in tasks:
                t_id = task['_id']
                parsed_id = task['parsed_id']

                if utils.time_print(int) - task['inquiry_time'] >= GLOBAL_VARS.TIMEOUT:
                    utils.print_log("{} has timedout...".format(t_id))
                    self._mongodb_c._db.tasks.update_many({"parsed_id": parsed_id}, {'$set': {'state': GLOBAL_VARS.TASK_STATES['TIMEOUT']}})
                    self._mongodb_c._db.queries.update_one({"_id": parsed_id}, {'$set': {'final_route': "ERROR"}})
                    # self._mongodb_c.update_one("queries", parsed_id, {"state": GLOBAL_VARS.TASK_STATES["TIMEOUT"],
                    #                                     "processed_time": utils.time_print(int)})
                    continue

                double_check = self._mongodb_c.find_one("tasks", query_dict = {'_id': t_id})
                if double_check:
                    if double_check['state'] > GLOBAL_VARS.TASK_STATES["SENT"]:
                        utils.print_log("{} already sent...".format(t_id))
                        continue
                    
                gridA = task['gridA']
                gridB = task['gridB']

                if isinstance(gridA, int):
                    rsu = gridB
                else:
                    rsu = gridA

                p_task = self.get_next_node_for_unsent_tasks(task['parsed_id'], task['step'], task['steps'])
                if p_task:
                    utils.print_log("Got next_node:{}".format(p_task['next_node']))
                    task['next_node'] = p_task['next_node']

                topic = utils.add_destination(GLOBAL_VARS.BROKER_TO_RSU, rsu)
                utils.print_log("Broker sending task {} to topic: {}".format(t_id, topic))
                payload = json.dumps(task)

                # "middleware/rsu/+; wild card subscription
                self._mongodb_c.update_one("tasks", t_id, {"state": GLOBAL_VARS.TASK_STATES["SENT"]})
                self.send(topic, utils.encode(payload))

            tasks = list(self._mongodb_c.find("tasks", {"state": {"$lte": GLOBAL_VARS.TASK_STATES["PROCESSED"]}}))
            # random.shuffle(tasks)
            # time.sleep(5)

    def get_next_node_for_unsent_tasks(self, parsed_id, step, steps):
        utils.print_log("get_next_node_for_unsent_tasks({}, {}, {})".format(parsed_id, step, steps))

        i_step = int(step)
        
        if i_step == 0:
            return None
        p_step = str(i_step - 1).zfill(3)
        q = {'parsed_id': parsed_id, 'step': p_step, 'steps':steps, 'state':GLOBAL_VARS.TASK_STATES["RESPONDED"]}
        # utils.print_log(q)
        prior_step = self._mongodb_c.find_one("tasks", query_dict=q)
        if prior_step:
            # utils.print_log(prior_step)
            return prior_step

    def start_collect_tasks_thread(self):
        if not self._collect_tasks.is_alive():
            print("Started compile_tasks_by_id thread.")
            self._collect_tasks = threading.Thread(target=self.compile_tasks_by_id, args = ())
            self._collect_tasks.start()
        else:
            print("compile_tasks_by_id thread already running.")

    # TODO: Add a timeout for queries too, trigger this thread when a message arrives, if count == 0, just die.
    '''
    Just run in a loop until all that exists is state:4, 98 or 99
    '''
    def compile_tasks_by_id(self):
        while True:
            time.sleep(5)
            count = self._mongodb_c._db.queries.count_documents({"final_route": None})
            if count == 0:
                continue
            res = self._mongodb_c._db.queries.find({"final_route": None})
            for r in res:
                parsed_id = r['_id']
                utils.print_log(parsed_id)
                count = self._mongodb_c._db.tasks.count_documents({"parsed_id": parsed_id, "state": 3})
                temps = self._mongodb_c._db.tasks.find_one({"parsed_id": parsed_id, "state": 3})
                if not temps:
                    continue

                task_steps = int(temps['steps']) + 1
                if task_steps == count:
                    tasks = self._mongodb_c._db.tasks.find({"parsed_id": parsed_id, "state": 3})
                    route = []
                    for task in tasks:
                        print("{}/{}".format(task['step'], task['steps']))
                        route.extend(task['route'])
                        last_processing_time = task['processed_time']

                    self._mongodb_c._db.queries.update_one({'_id': parsed_id}, 
                                                           {'$set': {'final_route': utils.f7(route), 
                                                                     'total_processed_time':last_processing_time}})

                    self._mongodb_c._db.tasks.update_many({"parsed_id": parsed_id, "state": 3}, {'$set': {'state': GLOBAL_VARS.TASK_STATES['COLLECTED']}})