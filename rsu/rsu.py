import json

from common.src.basic_utils import *
from src.Worker_Mqtt import Worker_Mqtt

if __name__ == "__main__":
    mqttc = Worker_Mqtt(host="mqtt")
    mqttc.connect()
    mqttc.start_sub_thread(["test/topic", 
                            "middleware/rsu/+"])