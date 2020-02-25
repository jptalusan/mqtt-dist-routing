import paho.mqtt.client as mqtt
import time
import json
import threading
from pprint import pprint

from common.src.mqtt_utils import MyMQTTClass
from common.src.mongo_class import MyMongoDBClass
from common.src.basic_utils import *
from common.conf import GLOBAL_VARS
from src.Broker_Mqtt import Broker_Mqtt

print(time.time())
print("HELLO")

# http://www.steves-internet-guide.com/mqtt-clean-sessions-example/

import os

if __name__ == "__main__":
    mongodbc = MyMongoDBClass(host="mongo", db="admin")
    mongodbc.get_client().is_mongos

    if __debug__ == 1:
        mongodbc.delete_all("tasks")

    mqttc = Broker_Mqtt(host="mqtt", mongodb_c=mongodbc)
    mqttc.connect()
    mqttc.start_sub_thread(["test/topic", 
                            GLOBAL_VARS.QUERY_TO_BROKER, 
                            GLOBAL_VARS.SUB_RESPONSE_TO_BROKER, 
                            GLOBAL_VARS.PROCESSED_TO_BROKER])