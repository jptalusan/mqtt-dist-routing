# TOPICS
BROKER_TO_RSU="middleware/rsu/"

QUERY_TO_BROKER="middleware/broker/task"
RESPONSE_TO_BROKER="middleware/broker/response"

ERROR_RESPONSE_TO_BROKER="middleware/broker/response/error_response"

SUB_RESPONSE_TO_BROKER="middleware/broker/response/+"
PROCESSED_TO_BROKER="middleware/processed/+"

SIMULATED_QUERY_TO_BROKER="middleware/broker/simulation_task"

ALLOCATION_STATUS_TO_RSU="middleware/status/"
ALLOCATION_STATUS_TO_BROKER="middleware/broker/status"

START_LOGGING="middleware/rsu/startlogging"
STOP_LOGGING="middleware/rsu/stoplogging"

TASK_STATES = {
                # OKS
                "UNSENT": 0,
                "SENT": 1,
                "ACK": 2,
                "PROCESSED": 3,
                "RESPONDED": 4,
                "COLLECTED": 5,
                
                # ERRORS
                "MAX_TRY": 97,
                "TIMEOUT": 98,
                "ERROR": 99
                }

# Routes get lost because of the limitations in the available nodes
# Some routes pass through boundaries that are at the corner of 4 grids/rsu
TIMEOUT = 300000
MAX_RETRIES = 200

RSUS = {"0000": "SPBbQt", "0005": "SPBY71", "0010": "SPEPyO", "0015": "SPBPqg", "0020": "SPBarz", 
        "0001": "SPBXhJ", "0006": "SPBZYd", "0011": "SPEPeO", "0016": "SPBb9J", "0021": "SPEO7z", 
        "0002": "SPB_DO", "0007": "SPB_r0", "0012": "SPBaCP", "0017": "SPBZuN", "0022": "SPE_Pa", 
        "0003": "SPEOdP", "0008": "SPBQ@b", "0013": "SPEP70", "0018": "SPBR6h", "0023": "SPBXxG", 
        "0004": "SPBYyN", "0009": "SPEOOK", "0014": "SPEPOe", "0019": "SPE_6g", "0024": "SPEOxP"}

WORKER = {"SPBbQt": "0000", "SPBY71": "0005", "SPEPyO": "0010", "SPBPqg": "0015", "SPBarz": "0020", 
          "SPBXhJ": "0001", "SPBZYd": "0006", "SPEPeO": "0011", "SPBb9J": "0016", "SPEO7z": "0021", 
          "SPB_DO": "0002", "SPB_r0": "0007", "SPBaCP": "0012", "SPBZuN": "0017", "SPE_Pa": "0022", 
          "SPEOdP": "0003", "SPBQ@b": "0008", "SPEP70": "0013", "SPBR6h": "0018", "SPBXxG": "0023", 
          "SPBYyN": "0004", "SPEOOK": "0009", "SPEPOe": "0014", "SPE_6g": "0019", "SPEOxP": "0024"}

RSU_ID = "RSU_ID"

#MongoDB Collections
TASKS = "tasks"
QUERIES = "queries"

LOG_RATE = 0.5 #in seconds

NEIGHBOR_LEVEL = 1
QUEUE_THRESHOLD = 5
DELAY_THRESHOLD = 5
