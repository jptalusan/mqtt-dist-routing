import sys
import networkx as nx
import pickle
import os
import time
import pandas as pd
from datetime import datetime
import json
import paho.mqtt.client as mqtt
import pprint
from multiprocessing import Pool
import multiprocessing as multi
import random
import argparse

sys.path.append('..')
from common.src import header as generator
from common.src.mqtt_utils import MyMQTTClass
from common.src.basic_utils import time_print
from common.conf import GLOBAL_VARS

def specify_task(task_list, parsed_id):
    new_list = []
    for t in task_list:
        if t.parsed_id == parsed_id:
            new_list.append(t)

    return new_list

def get_tasks(x, y, queries):
    start = time.time()

    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        raise OSError("Must first download data, see README.md")
    data_dir = os.path.join(os.getcwd(), 'data')

    file_path = os.path.join(data_dir, '{}-{}-G.pkl'.format(x, y))
    with open(file_path, 'rb') as handle:
        nx_g = pickle.load(handle)

    number_of_queries = queries

    file_path = os.path.join(data_dir, '{}-queries-for-{}-{}.pkl'.format(number_of_queries, x, y))
    if not os.path.exists(file_path):
        Qdf = generator.generate_query(nx_g, number_of_queries)
        a = generator.gen_SG(nx_g, Qdf)
        Qdf = Qdf.assign(og = a)

        task_list = generator.generate_tasks(Qdf)

        elapsed = time.time() - start
        print("Run time: {}".format(elapsed))

        file_path = os.path.join(data_dir, '{}-queries-for-{}-{}.pkl'.format(number_of_queries, x, y))
        pickle.dump(task_list, open(file_path,'wb'))
    else:
        task_list = pickle.load(open(file_path,'rb'))

    # This constant is true if Python was not started with an -O option
    if __debug__:
        [print(i, t.__dict__) for i, t in enumerate(task_list)]

    return task_list

def send_tasks(i, ts):
    print("Sending chunk: {} of size {}".format(i, len(ts)))
    mqttc = MyMQTTClass()
    mqttc.connect()
    mqttc.open()

    # task_list = specify_task(task_list, "b7c475b6")
    for t in ts:
    # for t in enumerate(task_list[0:1]):
    # for t in enumerate(task_list[1:2]):
        payload = {}
        payload['time_sent'] = time_print(0)
        # payload['data'] = t.get_json()
        payload['data'] = t.__dict__
        if __debug__:
            print(payload['data'])
        data = json.dumps(payload)
        mqttc.send(GLOBAL_VARS.QUERY_TO_BROKER, data)
        time.sleep(0.02)

    mqttc.close()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("a")
    args = parser.parse_args()
    x, y = 5, 5
    try:
        number_of_queries = int(args.a)
        mqttc = MyMQTTClass()
        mqttc.connect()
        mqttc.open()
        print("Query sent: {}".format(datetime.now().strftime("%d %b %Y %H:%M:%S.%f")))
        payload = {'x': x, 'y': y, 'number_of_queries': number_of_queries}
        print(payload)
        
        data = json.dumps(payload)
        mqttc.send(GLOBAL_VARS.SIMULATED_QUERY_TO_BROKER, data)
        mqttc.close()
    except ValueError:
        print("Enter an integer for number of queries.")
