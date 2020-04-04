import sys
import networkx as nx
import pickle
import os
import time
import pandas as pd
from datetime import datetime
import json
import pprint
from multiprocessing import Pool
import multiprocessing as multi
import random
from pathlib import Path

sys.path.append('..')
from common.src import header as generator
from common.src.basic_utils import time_print
from common.conf import GLOBAL_VARS

def specify_task(task_list, parsed_id):
    new_list = []
    for t in task_list:
        if t.parsed_id == parsed_id:
            new_list.append(t)

    return new_list

def generate_task_from_sdt(s, d, t):
    pass

def write_queries_to_mongodb(mongodb, query_df):
    print("write_queries_to_mongodb()")
    # print(query_df.head())
    # df = query_df[['t_id', 's', 'd', 't', 'r']].copy()
    query_df = query_df.rename(columns={"t_id": "_id", "r": "initial_route"})
    query_df['query_time'] = time_print(0)
    query_df['total_processed_time'] = None
    query_df['final_route'] = None
    query_df['total_travel_time'] = None
    # query_df['json'] = query_df.apply(lambda x: x.to_json(), axis=1)
    # print(new_df)

    # OK, but failing if record already exists.
    records = json.loads(query_df.T.to_json()).values()
    for record in records:
        t_id = record['_id']

        if mongodb._db.queries.count_documents({"_id": t_id}) == 0:
            mongodb._db.queries.insert(record)
        else:
            print("{} already exists.".format(t_id))
            
    print("Finished writing")

def get_single_task(mongodb, x, y, s, d, t):
    print("get_single_task({}, {}., ({}, {}, {}))".format(x, y, s, d, t))
    start = time_print(0)

    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        raise OSError("Must first download data, see README.md")
    data_dir = os.path.join(os.getcwd(), 'data')

    file_path = os.path.join(data_dir, '{}-{}-G.pkl'.format(x, y))
    
    print("CHECK1")
    with open(file_path, 'rb') as handle:
        nx_g = pickle.load(handle)

    print("CHECK2")
    Qdf = generator.generate_single_query(nx_g, s, d, t)
    print(Qdf)

    write_queries_to_mongodb(mongodb, Qdf)
    a = generator.gen_SG(nx_g, Qdf)
    Qdf = Qdf.assign(og = a)

    task_list = generator.generate_tasks(Qdf)

    elapsed = time_print(0) - start
    print("Run time: {} ms".format(elapsed))

    if sorted:
        task_list.sort(key=lambda x: x.step, reverse=False)
    return task_list


def get_tasks(mongodb, x, y, queries, sorted=True):
    print("get_tasks({}, {}, {})".format(x, y, queries))
    start = time_print(0)

    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        raise OSError("Must first download data, see README.md")
    data_dir = os.path.join(os.getcwd(), 'data')

    file_path = os.path.join(data_dir, '{}-{}-G.pkl'.format(x, y))
        
    with open(file_path, 'rb') as handle:
        nx_g = pickle.load(handle)

    number_of_queries = queries

    # res = generator.generate_single_query(nx_g, 1286, 1471, 22)
    # pprint(res)

    file_path = os.path.join(data_dir, '{}-queries-for-{}-{}.pkl'.format(number_of_queries, x, y))
    if not os.path.exists(file_path):
        Qdf = generator.generate_query(nx_g, number_of_queries)
        Qdf.to_pickle(file_path)
    else:
        Qdf = pd.read_pickle(file_path)

    write_queries_to_mongodb(mongodb, Qdf)

    a = generator.gen_SG(nx_g, Qdf)
    Qdf = Qdf.assign(og = a)

    task_list = generator.generate_tasks(Qdf)

    elapsed = time_print(0) - start
    print("Run time: {} ms".format(elapsed))

    if sorted:
        task_list.sort(key=lambda x: x.step, reverse=False)
    return task_list

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]




