import networkx as nx
import osmnx as ox
import pickle
import os
from os import listdir
from os.path import isfile, join
from shapely.geometry import Point
import pyproj    
from functools import partial
from shapely.geometry import shape
import shapely.ops as ops
import datetime

from .graph_breakdown import *

import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')

def generate_save_sub_graph(G, node_list, directory, filename=None):
    print("generate_save_sub_graph:", filename)
    SG = G.__class__()
    SG.add_nodes_from((n, G.nodes[n]) for n in node_list)
    if SG.is_multigraph:
        SG.add_edges_from((n, nbr, key, d)
            for n, nbrs in G.adj.items() if n in node_list
            for nbr, keydict in nbrs.items() if nbr in node_list
            for key, d in keydict.items())
    else:
        SG.add_edges_from((n, nbr, d)
            for n, nbrs in G.adj.items() if n in node_list
            for nbr, d in nbrs.items() if nbr in node_list)
    SG.graph.update(G.graph)
    
    SG = graph_breakdown.cleanup_graph(SG)
    file_path = os.path.join(directory + '/sub_graphs', filename)
    with open(file_path, 'wb') as handle:
        pickle.dump(SG, handle)
        
    return True

### Must create empty grids so the code doesn't break.
def create_sub_graphs_and_save(G, rsu_arr, directory):
    print("create_sub_graphs_and_save:", directory)
    empty_grids = []
    counter = 0
    grids = []

    for r in rsu_arr:
        grid = r.grid_id
    #     print(grid)
        poly_id = r.poly
        sub_graph_nodes = []
        for n in G.nodes:
            node = G.node[n]
            node_point = Point(node['x'], node['y'])
            if node_point.within(poly_id) or node_point.intersects(poly_id):
                sub_graph_nodes.append(n)
                
                # Must check if they are boundary nodes, and if grid is part of the list, if so: add them to sub_graph_nodes
            if 'is_bounds' in node and node['is_bounds'] == True:
                if grid in node['boundaries']:
                    sub_graph_nodes.append(n)

        if len(sub_graph_nodes) > 0:
            grids.append(grid)
            filename = str(counter).zfill(4) + '-' + grid + '.pkl'
            generate_save_sub_graph(G, sub_graph_nodes, directory, filename=filename)
            counter = counter + 1
        else:
            EG = nx.Graph()
            filename = str(counter).zfill(4) + '-' + grid + '.pkl'
            file_path = os.path.join(directory + '/sub_graphs', filename)
            with open(file_path, 'wb') as handle:
                pickle.dump(EG, handle)
            empty_grids.append(grid)
            counter = counter + 1

    print("Empty grids:")
    display(empty_grids)
    return empty_grids

def read_saved_sub_graphs(sub_graphs_dir):
    # This is just for the centralized archi

    grids = []
    sub_graph_dict = {}
    for f in listdir(sub_graphs_dir):
        if isfile(join(sub_graphs_dir, f)):
            if f == '.gitignore':
                continue
            grid_id = os.path.splitext(f)[0]
            grid_id = grid_id.split("-")[1]
            grids.append(grid_id)
            file_path = os.path.join(sub_graphs_dir, f)
            with open(file_path, 'rb') as handle:
                sub_graph = pickle.load(handle)
                sub_graph_dict[grid_id] = sub_graph
    return sub_graph_dict

def find_boundary_nodes(G, boundary_list):
    found_nodes = []
    for n in G.nodes():
        node = G.node[n]
        if 'is_bounds' in node:
            if node['is_bounds']:
                if set(node['boundaries']) == set(boundary_list):
                    found_nodes.append(n)
    return found_nodes

def get_grid_id_from_node(G, n):
    node = G.node[n]
    if 'grid_id' in node:
        return node['grid_id']
    

    if 'is_bounds' in node:
        if node['is_bounds']:
            return node['boundaries'][0]
    return None
        
def manhattan_distance(rsu1, rsu2):
    return sum(abs(a-b) for a,b in zip(rsu1.coords, rsu2.coords))

def get_rsu_by_grid_id(rsu_arr, grid_id):
    for r in rsu_arr:
        if r.grid_id == grid_id:
            return r
    return None

def get_km2_area(polygon):
    geom = polygon
    geom_area = ops.transform(
        partial(
            pyproj.transform,
            pyproj.Proj(init='EPSG:4326'),
            pyproj.Proj(
                proj='aea',
                lat_1=geom.bounds[1],
                lat_2=geom.bounds[3])),
        geom)

    # Print the area in m^2
    return geom_area.area / 1000000

def get_m2_area2(coordinate_list):
    lon, lat = zip(*coordinate_list)
    from pyproj import Proj
    pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")
    x, y = pa(lon, lat)
    cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
    from shapely.geometry import shape
    return shape(cop).area / 1000000