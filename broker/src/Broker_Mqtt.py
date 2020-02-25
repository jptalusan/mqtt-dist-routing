import json
import threading

import common.src.basic_utils as utils
from common.src.mqtt_utils import MyMQTTClass
from common.conf import GLOBAL_VARS
from pprint import pprint

class Broker_Mqtt(MyMQTTClass):
    def __init__(self, client_id=None, host="localhost", port=1883, keep_alive=60, clean_session=True, mongodb_c=None):
        super().__init__(client_id, host, port, keep_alive, clean_session)
        print("init broker mqtt")
        self._mongodb_c = mongodb_c

        self._timer_task = threading.Thread(target=self.get_unsent_tasks, args = ())
        self._timer_task.start()

    def mqtt_on_message(self, mqttc, obj, msg):
        # print("Inheritance:" + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        self.parse_topic(msg)

    def parse_topic(self, msg):
        t_arr = msg.topic.split("/")
        print(msg.topic)
        if msg.topic == GLOBAL_VARS.QUERY_TO_BROKER:
                print("Broker receives : {}".format(str(msg.payload)))
                self.generate_mongo_payload(msg.payload)

                self._timer_task = threading.Thread(target=self.get_unsent_tasks, args = ())
                self._timer_task.start()
                # if self._timer_task.is_alive():
                # else:
                #     print("dead\n")

        if GLOBAL_VARS.RESPONSE_TO_BROKER in msg.topic:
            rsu = t_arr[-1]
            print("RSU:", rsu)
            # Check if the name is RSU-XXXX
            if 'rsu' in rsu.lower():
                # update mongodb entry as Responded (2)
                data = json.loads(msg.payload)
                print("worker-{} responded with :{}".format(rsu, data['_id']))
                self._mongodb_c.update("tasks", data['_id'], {"state": GLOBAL_VARS.TASK_STATES["RESPONDED"]})
                pass

        if "middlleware" in t_arr and "processed" in t_arr:
            rsu = t_arr[-1]
            # Check if the name is RSU-XXXX
            if 'rsu' in rsu.lower():
                # update mongodb entry as Responded (2)
                pass

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
        t_id = data['_id']

        print("Finding:", t_id)
        _DB = self._mongodb_c.get_db("admin")
        found = _DB["tasks"].count_documents({"_id": t_id})
        if found == 0:
            t_id = self._mongodb_c.insert("tasks", data)
            print("inserted: {}".format(t_id))
        else:
            print("ID already exists")

    # maybe better to keep sending tasks until there is a response.
    # maybe change to while loop
    def get_unsent_tasks(self):
        print("get_unsent_tasks()")
        # threading.Timer(5.0, get_unsent_tasks, args=(mqttc, mongodbc,)).start()
        tasks = list(self._mongodb_c.find("tasks", {"state": {"$lt": GLOBAL_VARS.TASK_STATES["PROCESSED"]}}))
        while len(tasks) > 0:
            task = tasks.pop(0)
            t_id = task['_id']
            gridA = task['gridA']
            gridB = task['gridB']

            if isinstance(gridA, int):
                rsu = gridB
            else:
                rsu = gridA

            topic = utils.add_destination(GLOBAL_VARS.BROKER_TO_RSU, rsu)
            print("Broker sending to topic: {}".format(topic))
            payload = json.dumps(task)

            # "middleware/rsu/+; wild card subscription
            self._mongodb_c.update("tasks", t_id, {"state": GLOBAL_VARS.TASK_STATES["SENT"],
                                                   "processed_time": utils.time_print(int)})
            self.send(topic, utils.encode(payload))