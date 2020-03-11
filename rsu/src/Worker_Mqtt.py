from common.src.mqtt_utils import MyMQTTClass
import paho.mqtt.client as mqtt
from common.src.task import Task as Route_Task
from common.conf import GLOBAL_VARS
import common.src.basic_utils as utils
import json
from pprint import pprint
import threading
import time

class Worker_Mqtt(MyMQTTClass):
    def __init__(self, client_id=None, host="localhost", port=1883, keep_alive=60, clean_session=True, mongodb_c=None, route_extractor=None, log_file=None):
        super().__init__(client_id, host, port, keep_alive, clean_session)
        print("init worker mqtt")
        self._mongodb_c = mongodb_c
        self._client_id = client_id
        self._log_file = log_file
        self._tasks = []
        self._processed_tasks = []
        self._route_extractor = route_extractor
        self._current_processing = ""
        self._LOG_FLAG = True
        self._LOG_START_TIME = None

        self._timer_task = threading.Thread(target=self.process_tasks, args = ())
        self._timer_task.start()

    def mqtt_on_message(self, mqttc, obj, msg):
        self.parse_topic(msg)

    # TODO: Add method here to determine if task should be allocated here or not.
    def parse_topic(self, msg):
        t_arr = msg.topic.split("/")
        # print("RSU: {}".format(t_arr))

        # For logging only
        if msg.topic == GLOBAL_VARS.START_LOGGING:
            self._LOG_START_TIME = utils.time_print(0)
            self._logging_task = threading.Thread(target=self.logging_task, args = ())
            self._logging_task.start()
        if msg.topic == GLOBAL_VARS.STOP_LOGGING:
            self._LOG_FLAG = False
            log_dict = {}
            log_dict['time'] = utils.time_print(0)
            log_dict['queued_tasks'] = []
            log_dict['total_processed'] = list(set(self._processed_tasks))
            log_dict['timed_out'] = [task._id for task in self._tasks if task._id not in self._processed_tasks]
            utils.write_log(self._log_file, log_dict)

        if "middleware" in t_arr and "rsu" in t_arr:
            rsu = t_arr[-1]
            # If task is meant for this rsu
            # IF DEBUG
            # if rsu:
            if rsu == self._client_id:
                data = json.loads(msg.payload)
                print("RSU receives: ", data['_id'])
                res = self.verify_append_task(Route_Task(data))
                if res:
                    if not self._timer_task.is_alive():
                        print("Started process_tasks thread.")
                        self._timer_task = threading.Thread(target=self.process_tasks, args = ())
                        self._timer_task.start()
                    else:
                        print("process_tasks already running.")
                    
        return True
    
    # Update the next_node if possible
    def verify_append_task(self, task):
        if task._id in self._processed_tasks:
            print("Already processed.")
            return False

        ids_in_queue = [t._id for t in self._tasks]

        if task._id not in ids_in_queue:
            self._tasks.append(task)
            print("Appended {} to tasks".format(task._id))
            return True
        else:
            for t in self._tasks:
                if task._id == t._id:
                    if task.next_node is not None:
                        print("ID {} already exists, updated next_node".format(task._id))
                        t.next_node = task.next_node
                        print(t.__dict__)
                        return True
                    else:
                        print("Skipped {}".format(task._id))
                        return False
        return False
        
    def update_task(self, id):
        for _, task in enumerate(self._tasks):
            if task._id == id:
                task.state = GLOBAL_VARS.TASK_STATES["RESPONDED"]
                break

    def remove_task(self, id):
        for i, task in enumerate(self._tasks):
            if task._id == id:
                del self._tasks[i]
                break

    # TODO: Remove current processing (just put uynder load or something)
    # This achieves higher success rate. Why?
    def process_tasks(self):
        print("Processing {} tasks remaining".format(len(self._tasks)))
        while len(self._tasks) > 0:
            self._tasks = sorted(self._tasks, key=lambda k: int(k.step))

            t_dict = {}
            try:
                t = self._tasks.pop(0)
                t_dict = t.get_json()

                if t_dict['next_node'] is None and t_dict['step'] != '000':
                    utils.print_log("Cannot process {} yet.".format(t_dict['_id']))
                    return False

                if utils.time_print(0) - t_dict['inquiry_time'] >= GLOBAL_VARS.TIMEOUT:
                    return False

                route = self._route_extractor.find_route(t_dict)

                if route is None:
                    return False

                if all(route):
                    r = route[1]
                    r_int = [int(x) for x in r]
                    t_dict['route'] = r_int
                    t_dict['travel_time'] = route[0]
                    topic = utils.add_destination(GLOBAL_VARS.RESPONSE_TO_BROKER, self._client_id)
                    utils.print_log("Sending {} to {}".format(t_dict['_id'], topic))
                    utils.print_log("Removing {} from task queue and appending to processed_tasks".format(t_dict['_id']))
                    utils.print_log("{} Is done! with route: {}".format(t_dict['_id'], r_int))

                    self._processed_tasks.append(t_dict['_id'])
                    self.send(topic, json.dumps(t_dict))
                    
                    # self.remove_task(t_dict['_id'])
                    return True
                else:
                    return False
            except IndexError as e:
                print(e)

            # time.sleep(10)

    # Regularly log data until timeout
    def logging_task(self):
        while self._LOG_FLAG:
            log_dict = {}
            log_dict['time'] = utils.time_print(0)
            # log_dict['processing'] = self._current_processing
            log_dict['queued_tasks'] = [task._id for task in self._tasks if task._id not in self._processed_tasks]
            log_dict['total_processed'] = list(set(self._processed_tasks))
            log_dict['timed_out'] = []
            utils.write_log(self._log_file, log_dict)

            time.sleep(GLOBAL_VARS.LOG_RATE)
            if utils.time_print(0) - self._LOG_START_TIME > GLOBAL_VARS.TIMEOUT:
                self._LOG_FLAG = False
                break