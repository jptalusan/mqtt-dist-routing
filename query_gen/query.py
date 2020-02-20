import sys
import networkx as nx
import pickle
import os
import time
import pandas as pd
from datetime import datetime
import json
import paho.mqtt.client as mqtt

sys.path.append('..')
from common.src import header as generator
from common.src.mqtt_utils import MyMQTTClass
from common.src.basic_utils import time_print

start = time.time()

if not os.path.exists(os.path.join(os.getcwd(), 'data')):
    raise OSError("Must first download data, see README.md")
data_dir = os.path.join(os.getcwd(), 'data')

x, y = 5, 5

file_path = os.path.join(data_dir, '{}-{}-G.pkl'.format(x, y))
print(file_path)
with open(file_path, 'rb') as handle:
    nx_g = pickle.load(handle)
print(nx.__version__)
print(len(nx_g.nodes()))

# https://github.com/gboeing/osmnx/issues/363
# print(nx_g.nodes[0])

number_of_queries = 2
clean_session = False

file_path = os.path.join(data_dir, '{}-queries-for-{}-{}.pkl'.format(number_of_queries, x, y))
if not os.path.exists(file_path):
    Qdf = generator.generate_query(nx_g, number_of_queries)
    # print(Qdf.head())

    a = generator.gen_SG(nx_g, Qdf)
    Qdf = Qdf.assign(og = a)
    # print(Qdf.head())

    elapsed = time.time() - start
    print("Run time: {}".format(elapsed))

    file_path = os.path.join(data_dir, '{}-queries-for-{}-{}.pkl'.format(number_of_queries, x, y))
    generator.save_query_dataframe(Qdf, file_path)
else:
    Qdf = pd.read_pickle(file_path)

# Converting row to a json

# print("\nConverting to JSON")
# for i in Qdf.index:
#     print(i)
#     print(Qdf.loc[i].to_json("row{}.json".format(i)))

# Converting a row to json and adding it into a column named "json"
# Qdf['json'] = Qdf.apply(lambda x: x.to_json(), axis=1)

task_list = generator.generate_tasks(Qdf)

# If you want to use a specific client id, use
# mqttc = MyMQTTClass("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.

mqttc = MyMQTTClass()
mqttc.connect()

# Subscribing to some topic in a separate thread
# mqttc.start_sub_thread(["test/topic", "test/topic2"])

# Publishing messages, need to use mqttc.open() first??? I dont think so 
mqttc.open()
for count, t in enumerate(task_list):
    payload = {}
    payload['time_sent'] = time_print(0)
    payload['data'] = t.__dict__
    print(t.__dict__)
    data = json.dumps(payload)
    mqttc.send("middleware/broker/task", data)
    time.sleep(0.02)

mqttc.close()