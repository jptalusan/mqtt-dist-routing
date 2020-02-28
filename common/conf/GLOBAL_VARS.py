# TOPICS
BROKER_TO_RSU="middleware/rsu/"
QUERY_TO_BROKER="middleware/broker/task"
RESPONSE_TO_BROKER="middleware/broker/response"
ERROR_RESPONSE_TO_BROKER="middleware/broker/response/error_response"
SUB_RESPONSE_TO_BROKER="middleware/broker/response/+"
PROCESSED_TO_BROKER="middleware/processed/+"

TASK_STATES = {
                "ERROR": 99,
                "TIMEOUT": 98,
                "UNSENT": 0,
                "SENT": 1,
                "PROCESSED": 2,
                "RESPONDED": 3,
                "COLLECTED": 4
                }

# Routes get lost because of the limitations in the available nodes
# Some routes pass through boundaries that are at the corner of 4 grids/rsu
TIMEOUT = 30000