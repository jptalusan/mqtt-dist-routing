import datetime
import time
import random
import string

time_print = lambda type: datetime.now().strftime("%d/%m/%Y %H:%M:%S") if type == 'str' else int(round(time.time() * 1000))

decode = lambda x: x.decode('utf-8')
encode = lambda x: x.encode('ascii')

def add_destination(topic, dest):
    if topic[-1] == '/':
        # topic = topic[:-1]
        topic = topic + dest
    else:
        topic = topic + "/" + dest

    return topic

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def print_log(log, level=0, log_type="D"):
    d = datetime.datetime.utcnow().strftime("%d %b %Y %H:%M:%S.%f")[:-3]
    print("{}:{} {} # {}".format(level, log_type, d, log))