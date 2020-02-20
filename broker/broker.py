import paho.mqtt.client as mqtt
import time
import json
import threading
from pprint import pprint

from common.src.mqtt_utils import MyMQTTClass
from common.src.mongo_class import MyMongoDBClass
from common.src.basic_utils import *
from src.Broker_Mqtt import Broker_Mqtt

print(time.time())
print("HELLO")

# http://www.steves-internet-guide.com/mqtt-clean-sessions-example/

import os

# maybe better to keep sending tasks until there is a response.
def get_unsent_tasks(mqttc, mongodbc):
    print("get_unsent_tasks()")
    threading.Timer(5.0, get_unsent_tasks, args=(mqttc, mongodbc,)).start()
    tasks = mongodbc.find("tasks", {"processed": {"$lt": 2}})
    for task in tasks:
        t_id = task['_id']
        pprint(t_id)
        rsu = task['gridA']
        topic = "middleware/rsu/{}".format(rsu)
        payload = json.dumps(task)

        # "middleware/rsu/+; wild card subscription
        mongodbc.update("tasks", t_id, {"processed": 1})
        mqttc.send(topic, encode(payload))

if __name__ == "__main__":
    # hostname = "google.com"
    # response = os.system("ping -c 1 " + hostname)
    # if response == 0:
    #     print("Host is up")

    mongodbc = MyMongoDBClass(host="mongo", db="admin")
    mongodbc.get_client().is_mongos

    mqttc = Broker_Mqtt(host="mqtt", mongodb_c=mongodbc)
    mqttc.connect()
    mqttc.start_sub_thread(["test/topic", "middleware/broker/task"])
    
    get_unsent_tasks(mqttc, mongodbc)
    mqttc.send("test/topic", "TAE")
