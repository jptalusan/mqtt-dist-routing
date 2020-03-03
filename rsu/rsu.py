import json
import os
from common.src.basic_utils import *
from src.Worker_Mqtt import Worker_Mqtt
from src import Route_Executor as Route_Executor
from common.conf import GLOBAL_VARS

DEBUG = False
RSU_ID = os.getenv(GLOBAL_VARS.RSU_ID)
GRID_ID = GLOBAL_VARS.RSUS[RSU_ID]

if __name__ == "__main__":
    r_ex = Route_Executor.Route_Executor(x = 5, y = 5)
    print("GRID_ID:", GRID_ID)

    if DEBUG:
        client_id = 'rsu-' + randomString()
        mqttc = Worker_Mqtt(host="mqtt", client_id=client_id, route_extractor=r_ex)
        mqttc.connect()
        mqttc.start_sub_thread(["test/topic", 
                                "middleware/rsu/+"])
    else:
        client_id = GRID_ID
        mqttc = Worker_Mqtt(host="mqtt", client_id=client_id, route_extractor=r_ex)
        mqttc.connect()
        mqttc.start_sub_thread(["test/topic", 
                                "middleware/rsu/{}".format(GRID_ID)])
