import json
import os
from src.Worker_Mqtt import Worker_Mqtt
from src import Route_Executor as Route_Executor
from common.conf import GLOBAL_VARS
from common.src.mongo_class import MyMongoDBClass

DEBUG = False
RSU_ID = os.getenv(GLOBAL_VARS.RSU_ID)
GRID_ID = GLOBAL_VARS.RSUS[RSU_ID]

if __name__ == "__main__":
    # mongodbc = MyMongoDBClass(host="mongo", db="admin")

    r_ex = Route_Executor.Route_Executor(x = 5, y = 5)
    # r_ex.assign_mongodb(mongodbc)

    # print("GRID_ID:", GRID_ID)

    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        raise OSError("Must first download data, see README.md")
    data_dir = os.path.join(os.getcwd(), 'data')

    if not os.path.exists(os.path.join(data_dir, 'logs')):
        os.mkdir(os.path.join(data_dir, 'logs'))
    logs_dir = os.path.join(data_dir, 'logs')

    if DEBUG:
        client_id = 'rsu-' + randomString()
        log_file = os.path.join(logs_dir, '{}.csv'.format(client_id))
        try:
            os.remove(log_file)
        except OSError:
            pass
        mqttc = Worker_Mqtt(host="mqtt", client_id=client_id, route_extractor=r_ex, log_file=log_file)
    else:
        client_id = GRID_ID
        log_file = os.path.join(logs_dir, '{}.csv'.format(client_id))
        try:
            os.remove(log_file)
        except OSError:
            pass
        mqttc = Worker_Mqtt(host="mqtt", port=1883, client_id=client_id, route_extractor=r_ex, log_file=log_file, mongodb_c=None)

    mqttc.connect()
    mqttc.start_sub_thread(["TEST",
                            GLOBAL_VARS.START_LOGGING,
                            GLOBAL_VARS.STOP_LOGGING,
                            "{}{}".format(GLOBAL_VARS.ALLOCATION_STATUS_TO_RSU, GRID_ID), 
                            "{}{}".format(GLOBAL_VARS.BROKER_TO_RSU, GRID_ID), 
                            "{}{}".format(GLOBAL_VARS.RSU_TO_RSU, GRID_ID)])
