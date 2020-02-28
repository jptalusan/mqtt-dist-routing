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
        self.process_tasks()

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
            # Check if the name is RSU-XXXX
            # if 'rsu' in rsu.lower():
                # update mongodb entry as Responded (2)
            # print("worker received task from broker: {}".format(msg.payload))
            data = json.loads(msg.payload)
            print("RSU receives: ", data)
            r = Route_Task(data)
            print("ID: ", r._id)
            
            if not self.task_exists(r._id):
                print("Route Task id: ", r._id)
                self._tasks.append(r)
                    # self._timer_task = threading.Timer(5.0, self.process_tasks, args=()).start()
            else:
                print("ID {} already exists.".format(r._id))
        return True
    
    # Update the next_node if possible
    def task_exists(self, id):
        # if id in self._processed_tasks:
        #     return True
        
        if len(self._tasks) == 0:
            return False
        for t in self._tasks:
            if t._id == id:
                return True
        return False

    def process_tasks(self):
        print("Processing {} tasks remaining".format(len(self._tasks)))
        for t in self._tasks:
            utils.print_log("Task:{}".format(t._id))

        while len(self._tasks) > 0:
            t_dict = {}
            try:
                t = self._tasks.pop(0)
                t_dict = t.get_json()
                route = self._route_extractor.find_route(t_dict)
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