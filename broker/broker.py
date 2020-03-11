from common.src.mqtt_utils import MyMQTTClass
from common.src.mongo_class import MyMongoDBClass
from common.conf import GLOBAL_VARS
from src.Broker_Mqtt import Broker_Mqtt

# http://www.steves-internet-guide.com/mqtt-clean-sessions-example/

if __name__ == "__main__":
    mongodbc = MyMongoDBClass(host="mongo", db="admin")
    mongodbc.get_client().is_mongos

    if __debug__ == 1:
        mongodbc.delete_all(GLOBAL_VARS.TASKS)
        mongodbc.delete_all(GLOBAL_VARS.QUERIES)

    mqttc = Broker_Mqtt(host="mqtt", mongodb_c=mongodbc)
    mqttc.connect()
    mqttc.start_sub_thread([GLOBAL_VARS.QUERY_TO_BROKER, 
                            GLOBAL_VARS.SUB_RESPONSE_TO_BROKER, 
                            GLOBAL_VARS.PROCESSED_TO_BROKER,
                            GLOBAL_VARS.SIMULATED_QUERY_TO_BROKER,
                            GLOBAL_VARS.ALLOCATION_STATUS_TO_BROKER])