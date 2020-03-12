import json
import threading
import time
import src.query_generator as generator
import common.src.basic_utils as utils
from common.src.mqtt_utils import MyMQTTClass
from common.conf import GLOBAL_VARS
from pprint import pprint
import random
import pickle
import common.src.utility as geo_utils
import os
import common.src.adjustable_RSU as ag

class Broker_Mqtt(MyMQTTClass):
    def __init__(self, client_id=None, host="localhost", port=1883, keep_alive=60, clean_session=True, mongodb_c=None):
        super().__init__(client_id, host, port, keep_alive, clean_session)
        print("init broker mqtt")
        self._mongodb_c = mongodb_c

        self._tasks = []
        
        self._log_flag_once = False
        self._timer_task = threading.Thread(target=self.get_unsent_tasks, args = ())
        self._timer_task.start()
        
        self._collect_tasks = threading.Thread(target=self.compile_tasks_by_id, args = ())
        self._collect_tasks.start()

        self._heartbeat = threading.Thread(target=self.heartbeat, args = ())
        self._heartbeat.start()

        if not os.path.exists(os.path.join(os.getcwd(), 'data')):
            raise OSError("Must first download data, see README.md")
        data_dir = os.path.join(os.getcwd(), 'data')

        file_path = os.path.join(data_dir, '{}-{}-rsu_arr.pkl'.format(5, 5))
        with open(file_path, 'rb') as handle:
            self._rsu_arr = pickle.load(handle)

        file_path = os.path.join(data_dir, '{}-{}-G.pkl'.format(5, 5))
        with open(file_path, 'rb') as handle:
            self._nxg = pickle.load(handle)

    def mqtt_on_message(self, mqttc, obj, msg):
        # print("Inheritance:" + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        self.parse_topic(msg)


    def heartbeat(self):
        while True:
            self.send(GLOBAL_VARS.HEARTBEAT, utils.encode("HEARTBEAT"))
            time.sleep(3)

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
            
            self.generate_mongo_tasks_entry(tasks)
            for task in tasks:
                self.subtask_allocation(GLOBAL_VARS.NEIGHBOR_LEVEL, task)
            for task in tasks:
                self.assign_next_rsu(task)

            self._tasks = tasks

            self._log_flag_once = False
            self.send(GLOBAL_VARS.START_LOGGING, utils.encode("START"))

        if msg.topic == GLOBAL_VARS.QUERY_TO_BROKER:
                print("Broker receives : {}".format(str(msg.payload)))
                self.generate_mongo_payload(msg.payload)

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
                travel_time = data['travel_time']
                utils.print_log("worker-{} responded with :{}".format(rsu, data['_id']))
                self._mongodb_c.update_one("tasks", data['_id'], {"state": GLOBAL_VARS.TASK_STATES["RESPONDED"],
                                                              "processed_time": utils.time_print(int),
                                                              "travel_time": travel_time,
                                                              "route": route,
                                                              "next_node": route[-1]})
                utils.print_log("Updated: {}".format(data['_id']))
        
        if "middlleware" in t_arr and "processed" in t_arr:
            rsu = t_arr[-1]
            # Check if the name is RSU-XXXX
            if 'rsu' in rsu.lower():
                # update mongodb entry as Responded (2)
                pass

        self.start_unsent_tasks_thread()

    # TODO: Add assigned time maybe?
    # Place for adding new mongodb columns.
    # Unsent = 0, Sent = 1, Responded = 2, Task_done = 3
    def generate_mongo_tasks_entry(self, tasks):
        for task in tasks:
            data = task.get_json()
            data['inquiry_time'] = utils.time_print(int)
            data['allocation_time'] = None
            data['processed_time'] = None
            data['state'] = GLOBAL_VARS.TASK_STATES["UNSENT"]
            data['next_node'] = None
            data['route'] = None
            data['travel_time'] = None
            data['rsu_assigned_to'] = None
            data['retry_count'] = 0
            data['next_rsu'] = None
            t_id = data['_id']

            _DB = self._mongodb_c.get_db("admin")
            found = _DB["tasks"].count_documents({"_id": t_id})
            if found == 0:
                t_id = self._mongodb_c.insert("tasks", data)
            else:
                pass

    def generate_mongo_payload(self, message):
        print("generate_mongo_payload:", len(message))
        _m = utils.decode(message)
        _d = json.loads(_m)
        data = _d['data']
        data['inquiry_time'] = utils.time_print(int)
        data['allocation_time'] = None
        data['processed_time'] = None
        data['state'] = GLOBAL_VARS.TASK_STATES["UNSENT"]
        data['next_node'] = None
        data['route'] = None
        data['travel_time'] = None
        data['rsu_assigned_to'] = None
        data['retry_count'] = 0
        data['next_rsu'] = None
        t_id = data['_id']

        _DB = self._mongodb_c.get_db("admin")
        found = _DB["tasks"].count_documents({"_id": t_id})
        if found == 0:
            t_id = self._mongodb_c.insert("tasks", data)
        else:
            pass

    # TODO: If a subtask in the middle of a task is ERROR:99, change all the tasks to ERROR as well.
    # But if its the last of the subtask then its ok i guess.
    def check_errors(self):
        pass

    def remove_one_task(self, id):
        for i, task in enumerate(self._tasks):
            if task._id == id:
                del self._tasks[i]
                print("removed one ({})".format(id))
                break

    def remove_task(self, parsed_id):
        for i, task in enumerate(self._tasks):
            if task.parsed_id == parsed_id:
                del self._tasks[i]
                print("removed msny ({})".format(parsed_id))
                break

    def assign_next_rsu(self, subtask):
        # Get next sub-task step
        data = subtask.get_json()
        _id = data['_id']
        step = data['step']
        steps = data['steps']
        if step == steps:
            return
        next_step = str(int(step) + 1).zfill(3)
        parsed_id = data['parsed_id']
        res = self._mongodb_c._db.tasks.find_one({"parsed_id": parsed_id, "step": next_step})
        # Should always have a result if it is not the last step, if none, then it really is an error in the task generation
        next_rsu = res['rsu_assigned_to']
        self._mongodb_c._db.tasks.update_one({"_id": _id}, {"$set": {"next_rsu": next_rsu}})
        utils.print_log("Set to: {}".format(next_rsu))
        pass
        
    # Decide which RSU to allocate to by sending status queries
    def subtask_allocation(self, nlevel, subtask):
        data = subtask.get_json()
        gridA = data['gridA']
        gridB = data['gridB']

        if isinstance(gridA, int):
            optimal_rsu = gridB
        else:
            optimal_rsu = gridA
            
        if nlevel == 0:
            self._mongodb_c._db.tasks.update_one({"_id": data['_id']}, {'$set': {'rsu_assigned_to': optimal_rsu, 'allocation_time': utils.time_print(int)}})
            return

        elif nlevel == 1:
            r = geo_utils.get_rsu_by_grid_id(self._rsu_arr, optimal_rsu)
            nn = geo_utils.get_neighbors_level(self._rsu_arr, r.get_idx(), nlevel)
            # print("subtask_allocation: {}".format(r.grid_id))
            # utils.print_log("Neighbors: {}".format(nn))
            
            nn.insert(0, r.get_idx())
            found = False
            candidate_rsus = []
            for n in nn:
                rsu = self._rsu_arr[n]
                candidate_rsus.append(rsu)
                res = rsu.add_task(self._nxg, self._rsu_arr, subtask, force=False)
                if res:
                    found = True
                    self._mongodb_c._db.tasks.update_one({"_id": data['_id']}, {'$set': {'rsu_assigned_to': rsu.grid_id, 'allocation_time': utils.time_print(int)}})
                    break
                '''
                If not ok, move to the next one (keep which has lowest number)
                '''
            # Get RSU with least number of queue
            if not found:
                print("Not found by looking, must force...")
                candidate_rsus = sorted(candidate_rsus, key=lambda rsu: len(rsu.queue))
                candidate_rsus[0].add_task_forced(subtask)
                # print(candidate_rsus)
                grid_id = candidate_rsus[0].grid_id
                self._mongodb_c._db.tasks.update_one({"_id": data['_id']}, {'$set': {'rsu_assigned_to': grid_id, 'allocation_time': utils.time_print(int)}})
                    
            # TODO: remove once i am sure it works
            # time.sleep(5)
            return

    # TODO: Check or create a new mqtt topic for replying to broker's inquiry of how "loaded" the RSUs are (task queue length) as well as checking distance between optimal
    # What is the optimal grid? rsu below in line 120?
    def get_unsent_tasks(self):
        print("get_unsent_tasks()")
        # [utils.print_log(task._id) for task in self._tasks]
        mongo_tasks = list(self._mongodb_c.find("tasks", {"state": {"$lt": GLOBAL_VARS.TASK_STATES["SENT"]}}))
        time.sleep(0.2)

        # while len(tasks) > 0:
        while len(mongo_tasks) > 0:
            # self._tasks = sorted(self._tasks, key=lambda k: int(k.step))
            # for task in self._tasks:
            for task in mongo_tasks:
                if task['rsu_assigned_to'] is None:
                    continue

                t_id = task['_id']
                parsed_id = task['parsed_id']

                if task['retry_count'] > GLOBAL_VARS.MAX_RETRIES:
                    self._mongodb_c._db.tasks.update_one({"_id": t_id}, {'$set': {'state': GLOBAL_VARS.TASK_STATES['MAX_TRY']}})
                    q = self._mongodb_c._db.queries.count_documents({"_id": parsed_id, "final_route": None})
                    if q:
                        self._mongodb_c._db.queries.update_one({"_id": parsed_id}, {'$set': {'final_route': "ERROR", 'total_travel_time': "ERROR"}})
                    self.remove_one_task(t_id)
                    continue

                if utils.time_print(int) - task['inquiry_time'] >= GLOBAL_VARS.TIMEOUT:
                    # utils.print_log("{} has timedout...".format(t_id))
                    self._mongodb_c._db.tasks.update_many({"parsed_id": parsed_id}, {'$set': {'state': GLOBAL_VARS.TASK_STATES['TIMEOUT']}})
                    # TODO: Just add if statement to check if the final_route is not error first.
                    q = self._mongodb_c._db.queries.count_documents({"_id": parsed_id, "final_route": None})
                    if q:
                        self._mongodb_c._db.queries.update_one({"_id": parsed_id}, {'$set': {'final_route': "ERROR", 'total_travel_time': "ERROR"}})
                    self.remove_one_task(t_id)

                    # TODO: Not really sure which one runs at the end.. this or see below
                    if not self._log_flag_once:
                        self.send(GLOBAL_VARS.STOP_LOGGING, utils.encode("STOP"))
                        self._log_flag_once = True

                    self._mongodb_c.save_collection_to_json('queries')
                    self._mongodb_c.save_collection_to_json('tasks')
                    continue
            

                double_check = self._mongodb_c.find_one("tasks", query_dict = {'_id': t_id})
                if double_check:
                    if double_check['state'] > GLOBAL_VARS.TASK_STATES["SENT"]:
                        continue
                    
                rsu = task['rsu_assigned_to']

                topic = utils.add_destination(GLOBAL_VARS.BROKER_TO_RSU, rsu)
                utils.print_log("Broker sending task {} to topic: rsu-{}".format(t_id, utils.get_worker_from_topic(topic)))
                payload = json.dumps(task)

                # "middleware/rsu/+; wild card subscription
                self._mongodb_c.update_one("tasks", t_id, {"state": GLOBAL_VARS.TASK_STATES["SENT"]})

                # TODO: Need to see how to fix this.
                task['state'] = GLOBAL_VARS.TASK_STATES["SENT"]

                self._mongodb_c._db.tasks.update({'_id': t_id}, {'$inc': {'retry_count': 1}})
                self.send(topic, utils.encode(payload))

            mongo_tasks = list(self._mongodb_c.find("tasks", {"state": {"$lt": GLOBAL_VARS.TASK_STATES["SENT"]}}))
            # random.shuffle(tasks)
            time.sleep(5)

    def get_next_node_for_unsent_tasks(self, parsed_id, step, steps):
        utils.print_log("get_next_node_for_unsent_tasks({}, {}, {})".format(parsed_id, step, steps))
        i_step = int(step)
        if i_step == 0:
            return None
        p_step = str(i_step - 1).zfill(3)
        q = {'parsed_id': parsed_id, 'step': p_step, 'steps':steps, 'state':GLOBAL_VARS.TASK_STATES["RESPONDED"]}

        prior_step = self._mongodb_c.find_one("tasks", query_dict=q)
        if prior_step:
            return prior_step

    # TODO: Add a timeout for queries too, trigger this thread when a message arrives, if count == 0, just die.
    # For debugging, just stop this once we finished processing all tasks (STOP_LOGGING)
    '''
    Just run in a loop until all that exists is state:4, 98 or 99
    '''
    def compile_tasks_by_id(self):
        while True:
            count = self._mongodb_c._db.queries.count_documents({"final_route": None})
            if count == 0:
                continue

            res = self._mongodb_c._db.queries.find({"final_route": None})
            for r in res:
                parsed_id = r['_id']
                # utils.print_log(parsed_id)
                count = self._mongodb_c._db.tasks.count_documents({"parsed_id": parsed_id, "state": GLOBAL_VARS.TASK_STATES["RESPONDED"]})
                temps = self._mongodb_c._db.tasks.find_one({"parsed_id": parsed_id, "state": GLOBAL_VARS.TASK_STATES["RESPONDED"]})

                if not temps:
                    continue

                task_steps = int(temps['steps']) + 1
                if task_steps == count:
                    tasks = self._mongodb_c._db.tasks.find({"parsed_id": parsed_id, "state": GLOBAL_VARS.TASK_STATES["RESPONDED"]})
                    route = []
                    total_travel_time = 0
                    for task in tasks:
                        print("{}/{}".format(task['step'], task['steps']))
                        route.extend(task['route'])
                        last_processing_time = task['processed_time']
                        total_travel_time = total_travel_time + task['travel_time']

                    self._mongodb_c._db.queries.update_one({'_id': parsed_id}, 
                                                            {'$set': {'final_route': utils.f7(route), 
                                                                    'total_processed_time':last_processing_time,
                                                                    'total_travel_time': total_travel_time}})

                    self._mongodb_c._db.tasks.update_many({"parsed_id": parsed_id, "state": GLOBAL_VARS.TASK_STATES["RESPONDED"]}, {'$set': {'state': GLOBAL_VARS.TASK_STATES['COLLECTED']}})
                    # self._mongodb_c._db.tasks.update_many({"parsed_id": parsed_id}, {'$set': {'state': GLOBAL_VARS.TASK_STATES['COLLECTED']}})

                    # self.remove_task(parsed_id)

                    # self.send(GLOBAL_VARS.STOP_LOGGING, utils.encode("STOP"))
                    # self._mongodb_c.save_collection_to_json('queries')
                    # self._mongodb_c.save_collection_to_json('tasks')
            # time.sleep(5)