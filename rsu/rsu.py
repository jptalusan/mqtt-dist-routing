import json

from common.src.basic_utils import *
from src.Worker_Mqtt import Worker_Mqtt
from src import Route_Executor as Route_Executor

if __name__ == "__main__":
    r_ex = Route_Executor.Route_Executor(x = 5, y = 5)
    
    client_id = 'rsu-' + randomString()
    mqttc = Worker_Mqtt(host="mqtt", client_id=client_id, route_extractor=r_ex)
    mqttc.connect()
    mqttc.start_sub_thread(["test/topic", 
                            "middleware/rsu/+"])
