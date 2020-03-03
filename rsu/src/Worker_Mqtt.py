from common.src.mqtt_utils import MyMQTTClass
import paho.mqtt.client as mqtt
from common.src.task import Task as Route_Task
from common.conf import GLOBAL_VARS
import common.src.basic_utils as utils
import json
from pprint import pprint
import threading
import time

class Worker_Mqtt(MyMQTTClass):
    def __init__(self, client_id=None, host="localhost", port=1883, keep_alive=60, clean_session=True, mongodb_c=None, route_extractor=None):
        super().__init__(client_id, host, port, keep_alive, clean_session)
        # self._mqttc = mqtt.Client(client_id=client_id, clean_session=clean_session)
        print("init worker mqtt")
        self._mongodb_c = mongodb_c
        self._client_id = client_id
        self._tasks = []
        self._processed_tasks = []

        self._timer_task = threading.Thread(target=self.process_tasks, args = ())
        self._timer_task.start()

        self._route_extractor = route_extractor

    def mqtt_on_message(self, mqttc, obj, msg):
        # print("Worker receives:" + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        self.parse_topic(msg)
        if not self._timer_task.is_alive():
            self._timer_task = threading.Thread(target=self.process_tasks, args = ())
            self._timer_task.start()

    # TODO: Add method here to determine if task should be allocated here or not.
    def parse_topic(self, msg):
        t_arr = msg.topic.split("/")
        print("RSU: {}".format(t_arr))
        if "middleware" in t_arr and "rsu" in t_arr:
            rsu = t_arr[-1]
            # If task is meant for this rsu
            # IF DEBUG
            # if rsu:
            if rsu == self._client_id:
                data = json.loads(msg.payload)
                print("RSU receives: ", data['_id'])
                res = self.verify_append_task(Route_Task(data))
                if res:
                    if not self._timer_task.is_alive():
                        print("Started process_tasks thread.")
                        self._timer_task = threading.Thread(target=self.process_tasks, args = ())
                        self._timer_task.start()
                    else:
                        print("process_tasks already running.")
                    
        return True
    
    # Update the next_node if possible
    def verify_append_task(self, task):
        ids_in_queue = [t._id for t in self._tasks]
        if task._id not in ids_in_queue:
            self._tasks.append(task)
            print("Appended {} to tasks".format(task._id))
            return True
        else:
            for t in self._tasks:
                if task._id == t._id:
                    if task.next_node is not None:
                        print("ID {} already exists, updated next_node".format(task._id))
                        t.next_node = task.next_node
                        print(t.__dict__)
                        return True
                    else:
                        print("Skipped {}".format(task._id))
                        return False
        return False
        
    def remove_task(self, id):
        print("remove_task({})".format(id))
        print("Tasks:", self._tasks)

        for i, task in enumerate(self._tasks):
            print(task._id)
            print(id)
            print(i)
            if task._id == id:
                del self._tasks[i]
                break
        print("Tasks:", self._tasks)
    # Task priority:If no viable tasks, then the process can sleep/wait
    '''
        1. Tasks with step == 000
        2. Tasks with next_node not None
        3. Everything else (should not be processed, just sorted)
    '''
    def get_viable_tasks(self):
        print("get_viable_tasks()")
        step_zeros = []
        next_nodes = []

        step_zeros = [t for t in self._tasks if t.step == '000']
        next_nodes = [t for t in self._tasks if t.next_node is not None and t.step != '000']
        # left_nodes = [t for t in self._tasks if t.next_node is None and t.step != '000']
        
        print("step_zeros:", step_zeros)
        [pprint(s.__dict__) for s in step_zeros]
        print("next_nodes:")
        [pprint(n.__dict__) for n in next_nodes]
        # print("left_nodes:")
        # [pprint(n.__dict__) for n in left_nodes]
        return step_zeros + next_nodes# + left_nodes


    # Loop through all tasks
    '''
    Pop task only when successful in getting route
    Lower completion rate but this is the correct way i think?
    because it holds the task
    '''
    def _process_tasks(self):
        print("process_tasks()")
        tasks = self.get_viable_tasks()
        while len(tasks) > 0:
            print("inside while")
            # t = tasks.pop(0)
            t = tasks[0]
            t_dict = t.get_json()
            print("processing...")
            print(t_dict)
            route = self._route_extractor.find_route(t_dict)
            if route is None:
                return False

            if all(route):
                r = route[1]
                r_int = [int(x) for x in r]
                t_dict['route'] = r_int
                topic = utils.add_destination(GLOBAL_VARS.RESPONSE_TO_BROKER, self._client_id)
                utils.print_log("Sending {} to {}".format(t_dict['_id'], topic))
                utils.print_log("Removing {} from task queue and appending to processed_tasks".format(t_dict['_id']))
                utils.print_log("{} Is done! with route: {}".format(t_dict['_id'], r_int))
                # self._processed_tasks.append(t_dict['_id'])
                self.send(topic, json.dumps(t_dict))
                self.remove_task(t_dict['_id'])
                tasks.pop(0)

                return True
            else:
                return False
            # time.sleep(5)

    # This achieves higher success rate. Why?
    def process_tasks(self):
        print("Processing {} tasks remaining".format(len(self._tasks)))
        for t in self._tasks:
            utils.print_log("Task:{}".format(t._id))
        # TODO: Sort the tasks at least?
        while len(self._tasks) > 0:
            self._tasks = sorted(self._tasks, key=lambda k: int(k.step))
            t_dict = {}
            try:
                t = self._tasks.pop(0)
                t_dict = t.get_json()
                route = self._route_extractor.find_route(t_dict)
                if route is None:
                    return False

                if all(route):
                    r = route[1]
                    r_int = [int(x) for x in r]
                    t_dict['route'] = r_int
                    topic = utils.add_destination(GLOBAL_VARS.RESPONSE_TO_BROKER, self._client_id)
                    utils.print_log("Sending {} to {}".format(t_dict['_id'], topic))
                    utils.print_log("Removing {} from task queue and appending to processed_tasks".format(t_dict['_id']))
                    utils.print_log("{} Is done! with route: {}".format(t_dict['_id'], r_int))
                    # self._processed_tasks.append(t_dict['_id'])
                    self.send(topic, json.dumps(t_dict))
                    return True
                else:
                    return False
            except IndexError as e:
                print(e)

            # time.sleep(2)