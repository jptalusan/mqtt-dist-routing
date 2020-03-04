# TOPICS
BROKER_TO_RSU="middleware/rsu/"
QUERY_TO_BROKER="middleware/broker/task"
RESPONSE_TO_BROKER="middleware/broker/response"
ERROR_RESPONSE_TO_BROKER="middleware/broker/response/error_response"
SUB_RESPONSE_TO_BROKER="middleware/broker/response/+"
PROCESSED_TO_BROKER="middleware/processed/+"
SIMULATED_QUERY_TO_BROKER="middleware/broker/simulation_task"

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

RSUS = {"0000": "SPBbQt", "0005": "SPBY71", "0010": "SPEPyO", "0015": "SPBPqg", "0020": "SPBarz", 
        "0001": "SPBXhJ", "0006": "SPBZYd", "0011": "SPEPeO", "0016": "SPBb9J", "0021": "SPEO7z", 
        "0002": "SPB_DO", "0007": "SPB_r0", "0012": "SPBaCP", "0017": "SPBZuN", "0022": "SPE_Pa", 
        "0003": "SPEOdP", "0008": "SPBQ@b", "0013": "SPEP70", "0018": "SPBR6h", "0023": "SPBXxG", 
        "0004": "SPBYyN", "0009": "SPEOOK", "0014": "SPEPOe", "0019": "SPE_6g", "0024": "SPEOxP"}

RSU_ID = "RSU_ID"

#MongoDB Collections
TASKS = "tasks"
QUERIES = "queries"