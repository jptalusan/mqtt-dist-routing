import random
import networkx as nx
import pandas as pd
import uuid
import copy
from .task import Task

# This is the entirety of query generation because the SG needs to be "pre-determined" before processing
# (since we dont have any model that would tell us the next best grid right now)
# Maybe creating a dataframe will be easier here.
# Generates a dataframe with columns (s, d, t, r)
'''
*s: source node
*d: destination node
*t: departure time
*r: route
'''
def generate_query(G, no_of_queries):
    Q = []
    routes = []
    for _ in range(no_of_queries):
        while len(routes) != no_of_queries:
            orig_node = random.choice(list(G.nodes))
            dest_node = random.choice(list(G.nodes))
            if orig_node == dest_node:
                continue
            try:
                q = {}
                q['s'] = orig_node
                q['d'] = dest_node
                time = random.randint(0, 23)
                q['t'] = time
                route = nx.shortest_path(G, orig_node, dest_node)
                print('Path: {}:{}'.format(orig_node, dest_node))
                routes.append(route)
                q['r'] = route
                Q.append(q)
            except nx.NetworkXNoPath:
#                 print('No path: {}:{}'.format(orig_node, dest_node))
                pass
    return pd.DataFrame(Q)

# Measure the number of routes that exist in only 1 grid maybe
# [s, x    , d]
# grid_id is not always available?
def gen_SG(G, Qdf):
    sg_list = []
    for index, row in Qdf.iterrows():
        route = row['r']
        sg = []
        for i, n in enumerate(route):
            node = G.nodes[n]
            if i == 0 or i == len(route) - 1:
                if 'grid_id' in node:
                    if node['grid_id'] not in sg:
                        sg.append(node['grid_id'])
                
            if 'is_bounds' in node:
                if node['is_bounds']:
#                     print(n, '\t', node['boundaries'])
                    pass
                else:
#                     print(n, '\t', node['grid_id'])
                    if node['grid_id'] not in sg:
                        sg.append(node['grid_id'])
#         print("\n")
        sg_list.append(list(sg))
    return sg_list

def save_query_dataframe(df, path):
    df.to_pickle(path)
    return True

def get_trunc_task_id(t_id):
        return '{:8.8}'.format(str(t_id))

# ID, Node, Grid1, Grid2, Time
def generate_tasks(Qdf): 
    task_list = []
    for index, row in Qdf.iterrows():
        t_id = uuid.uuid1()
        og = copy.copy(row['og'])
        s = row.s
        d = row.d
        t = row.t
        
        if len(og) >= 2:
            nodes = []
            nodes.append(s)
            nodes.extend([None] * (len(og) - 2))
            nodes.append(d)
            og.append(None)

#             # [t] * len(og) -> Assigns time variable to each pair
            ids = ["{}{}{}".format(get_trunc_task_id(t_id), 
                                    str(i).zfill(3), 
                                    str(len(og) - 2).zfill(3)) for i in range(len(og) - 1)]
            pairs = zip(ids, nodes, og, og[1:], [t] * len(og))
        elif len(og) == 1:
            id_ = "{}{}{}".format(get_trunc_task_id(t_id), 
                                    str(0).zfill(3), 
                                    str(0).zfill(3))
            pairs = zip([id_], [s], [d], [og[0]], [t])
            pass
        
        [task_list.append(Task(p)) for p in list(pairs)]
        task_list.extend(list(pairs))
    return task_list