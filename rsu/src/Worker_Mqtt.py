from common.src.mqtt_utils import MyMQTTClass
import common.src.basic_utils as utils
import json
from pprint import pprint

class Worker_Mqtt(MyMQTTClass):
    def __init__(self, client_id=None, host="localhost", port=1883, keep_alive=60, clean_session=True, mongodb_c=None):
        super().__init__(client_id, host, port, keep_alive, clean_session)
        print("init worker mqtt")
        self._mongodb_c = mongodb_c

        # self._mongodb_c.insert("HEY")

    def mqtt_on_message(self, mqttc, obj, msg):
        # print("Inheritance:" + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        self.parse_topic(msg)

    def parse_topic(self, msg):
        t_arr = msg.topic.split("/")
        print("RSU: {}".format(t_arr))
        if "middleware" in t_arr and "rsu" in t_arr:
            rsu = t_arr[-1]
            # Check if the name is RSU-XXXX
            # if 'rsu' in rsu.lower():
                # update mongodb entry as Responded (2)
            print("worker received task from broker: {}".format(msg.payload))

        return True

    # Unsent = 0, Sent = 1, Responded = 2, Task_done = 3
    def generate_mongo_payload(self, message):
        _m = utils.decode(message)
        _d = json.loads(_m)
        data = _d['data']
        data['processed'] = 0
        data['next_node'] = None
        t_id = data['_id']
        data['step'] = t_id[-6:-3]
        data['steps'] = t_id[-3:]
        data['t_id'] = t_id[0:-6]

        print("Finding:", t_id)
        _DB = self._mongodb_c.get_db("admin")
        found = _DB["tasks"].count_documents({"_id": t_id})
        if found == 0:
            t_id = self._mongodb_c.insert("tasks", data)
            print("inserted: {}".format(t_id))
        else:
            print("ID already exists")