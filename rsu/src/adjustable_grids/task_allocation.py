import random
import networkx as nx
import pandas as pd

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
            node = G.node[n]
#             print(node)
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
