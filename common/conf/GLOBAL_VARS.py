# TOPICS
BROKER_TO_RSU="middleware/rsu/"
QUERY_TO_BROKER="middleware/broker/task"
RESPONSE_TO_BROKER="middleware/broker/response"
SUB_RESPONSE_TO_BROKER="middleware/broker/response/+"
PROCESSED_TO_BROKER="middleware/processed/+"

TASK_STATES = {
                "UNSENT": 0,
                "SENT": 1,
                "PROCESSED": 2,
                "RESPONDED": 3,
                "COLLECTED": 4
                }