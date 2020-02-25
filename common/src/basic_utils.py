import datetime
import time

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