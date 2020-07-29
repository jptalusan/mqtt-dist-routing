import pickle
import networkx as nx
import osmnx as ox
import os
import random
import time

# Confirm directorys are in place
if not os.path.exists(os.path.join(os.getcwd(), 'benchmarks/data')):
    raise OSError("Must first download data, see README.md")
data_dir = os.path.join(os.getcwd(), 'data')

# Loading nx_g to save time for now...
file_path = os.path.join(data_dir, '5-5-G.pkl')
with open(file_path, 'rb') as handle:
    nx_g = pickle.load(handle)

number_of_queries = 1000
x, y = 5, 5
file_path = os.path.join(data_dir, '{}-queries-for-{}-{}.pkl'.format(number_of_queries, x, y))
task_list = pickle.load(open(file_path,'rb'))
print(task_list.head())

for run in range(3):
    print("Run: ", run)
    for j in range(10):
        start = time.time()
    #     print(j)
        for i, row in task_list.iterrows():
            s = row['s']
            d = row['d']

            r = nx.shortest_path(nx_g, s, d)
        #     print(i)
        elapsed = time.time() - start
        print(elapsed)