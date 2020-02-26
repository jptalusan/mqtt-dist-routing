import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import time
import os
import pandas as pd
import numpy as np
import pickle
import json
import random
import math
import time
import datetime
import sys
import copy

from os import listdir
from os.path import isfile, join

import networkx as nx
import osmnx as ox

import geohash_hilbert as ghh

from src.conf import LOCAL_RSU_VARS
from src import adjustable_grids as ag
import common.src.basic_utils as utils

DEBUG = False

class Route_Executor():
    def __init__(self, x, y):
        print("Route_Executor:__init__")
        if not os.path.exists(os.path.join(os.getcwd(), 'data')):
            raise OSError("Must first download data, see README.md")
        data_dir = os.path.join(os.getcwd(), 'data')

        if not os.path.exists(os.path.join(data_dir, 'sub_graphs')):
            os.mkdir(os.path.join(data_dir, 'sub_graphs'))
        sub_graphs_dir = os.path.join(data_dir, 'sub_graphs')

        if not os.path.exists(os.path.join(data_dir, 'avg_speeds')):
            os.mkdir(os.path.join(data_dir, 'avg_speeds'))
        self.avg_speeds_dir = os.path.join(data_dir, 'avg_speeds')

        print(sub_graphs_dir)
        self.sub_graph_dict = ag.read_saved_sub_graphs(sub_graphs_dir)
        # print(self.sub_graph_dict)

        target_area = LOCAL_RSU_VARS.EXTENDED_DOWNTOWN_NASH_POLY
        # Polys are just the larger boundaries to be used to "decrease" the number since we still use geohashing and it is still limited.
        polys = ag.divide_grid(target_area, (x, y))

        # some details
        print("Total Target area: {} km2".format(ag.get_km2_area(target_area)))
        print("Grids: {} km2".format(ag.get_km2_area(polys[0])))

        self.rsu_arr = []
        for i in range(x):
            for j in range(y):
                idx = j + (i * y)
                p = polys[idx]
                gid = ghh.encode(p.centroid.x, p.centroid.y, precision=6)
                r = ag.adjustable_RSU(gid, p, (i, j))
                r.set_max_size(x, y)
                self.rsu_arr.append(r)
        # Find what are the things needed to perform the route execution

    def find_route(self, task):
        print("Find_route of task: ", task)
        # Assuming first all tasks are assigned to one single RSU
        # Add checking for task Id so can reset the visualization
        # task_queue = task_list[8:14]

        next_node = task['next_node']
        task_id = task['_id']
        n = task['node']
        gA = task['gridA']
        gB = task['gridB']
        t = task['time_window']
        parsed_id = task['parsed_id']
        task_count = int(task['step'])
        task_length = int(task['steps'])

        if next_node is None and (task_count != 0 and task_length != 0):
            print("Error: Need to get the next_node value first.")
            return None

        if next_node is None:
            r = self.get_task_route(node1=n, gridA=gA, gridB=gB, node2=None, time=t)
            print("{}-node1: {}, gridA: {}, gridB: {}, node2: None, time: {}".
                format(task_count, n, gA, gB, t))
        elif next_node:
            r = self.get_task_route(node1=n, gridA=gA, gridB=gB, node2=next_node, time=t)
            print("{}-node1: {}, gridA: {}, gridB: {}, node2: {}, time: {}".
                format(task_count, n, gA, gB, next_node, t))
        print(r)
        return r

    def get_avg_speed_at_edge(self, start, end, attr, sensor_data=None, time_window=None):
        if 0 not in attr:
            key = random.choice(list(attr))
            tmc_id = attr[key]['tmc_id']
            length = attr[key]['length']
        else:
            tmc_id = attr[0]['tmc_id']
            length = attr[0]['length']
        
        if tmc_id in sensor_data:
            average_speed_at_time_window = sensor_data[tmc_id]['speeds'][time_window]
            time_traversed = length / average_speed_at_time_window
            return time_traversed
        # Default just so it runs!
        return 10

    def random_speeds(self, start, end, attr, sensor_data=None, time_window=None):
        if 0 not in attr:
            key = random.choice(list(attr))
            tmc_id = attr[key]['tmc_id']
        else:
            tmc_id = attr[0]['tmc_id']
        average_speed_at_time_window = random.uniform(1, 100)
        return average_speed_at_time_window

    def get_speeds_hash_for_grid(self, grid_id, with_neighbors=False):
        #     print("get_speeds_hash_for_grid(grid_id={})".format(grid_id))
        G = {}
        file_path = os.path.join(self.avg_speeds_dir, '{}-avg_speeds.pkl'.format(grid_id))
        with open(file_path, 'rb') as handle:
            g = pickle.load(handle)
            G = {**G, **g}
        if with_neighbors and self.rsu_arr:
            r = ag.get_rsu_by_grid_id(self.rsu_arr, grid_id)
            d = r.get_neighbors(self.rsu_arr)
            sg = self.sub_graph_dict[grid_id]

            for k, n in d.items():
                if n:
                    grid_id = n.grid_id
        #             print(grid_id)
                    file_path = os.path.join(self.avg_speeds_dir, '{}-avg_speeds.pkl'.format(grid_id))
                    with open(file_path, 'rb') as handle:
                        g = pickle.load(handle)
                        G = {**G, **g}
        return G

    # TODO: Find least time between 2 grids
    # using custom networkx
    def get_bounds_between_two_grids(self, grid1, grid2):
        possible_nodes = []
        sg1 = self.sub_graph_dict[grid1]
        sg2 = self.sub_graph_dict[grid2]
        
        for n in sg1.nodes:
            node = sg1.node[n]
            if 'is_bounds' in node and node['is_bounds']:
                boundaries = node['boundaries']
                if set([grid1, grid2]) == set(boundaries):
    #                 print(n, node)
                    if n not in possible_nodes:
                        possible_nodes.append(n)
                        
    #     print("\n")

        for n in sg2.nodes:
            node = sg2.node[n]
            if 'is_bounds' in node and node['is_bounds']:
                boundaries = node['boundaries']
                if set([grid1, grid2]) == set(boundaries):
    #                 print(n, node)
                    if n not in possible_nodes:
                        possible_nodes.append(n)
    #     print(sg1, sg2)
        return possible_nodes
        
    def get_shortest_route(self, sg, grid, node, bounds_list):
        # Assume that rsu_arr is present in the rsu
        G = self.get_speeds_hash_for_grid(grid, with_neighbors=True)
        fastest = math.inf
        route = None
        for b in bounds_list:
            try:
                (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node, b, self.get_avg_speed_at_edge, G, time_window=10)
                if total_time < fastest:
                    fastest = total_time
                    route = avg_speed_route
            except nx.NetworkXNoPath:
    #             print("No path: {}-{}".format(node, b))
                pass
            except nx.NodeNotFound as e:
                utils.print_log("Error: {}".format(e))
    #         print(total_time, route)

        if route == None:
            return None, None
    #     print(total_time, route)
        return (total_time, route)
            
    # TODO: use table above
    # Node 2 is the node from the previous hop/route
    def get_task_route(self, node1, gridA, gridB, time, node2=None):
        if (node1 is None) and ((gridA is None) or (gridB is None)):
            print("False")
            return False
        elif node1 is not None and (gridA is not None and isinstance(gridA, str)) and (gridB is not None and isinstance(gridB, str)):
            # First hop (use node1 and the boundary )
            if DEBUG:
                print("Task A")
            bounds = self.get_bounds_between_two_grids(gridA, gridB)
            (total_time, route) = self.get_shortest_route(self.sub_graph_dict[gridA], gridA, node1, bounds)
    #         print(total_time, route)
            return total_time, route
            
        elif node1 is None and (gridA is not None and isinstance(gridB, str)) and (gridB is not None and isinstance(gridB, str)):
            # Middle hop: must make use of node2 (the result of the previous hop)
            if DEBUG:
                print("Task B")
            bounds = self.get_bounds_between_two_grids(gridA, gridB)
            (total_time, route) = self.get_shortest_route(self.sub_graph_dict[gridA], gridA, node2, bounds)
    #         print(total_time, route)
            return total_time, route
        
        elif node1 is not None and gridA is not None and gridB is None:
            # Last hop: must make use of node2 (the result of the previous hop)

            if DEBUG:
                print("Task C")
            
            # Assume that rsu_arr is present in the rsu
            G = self.get_speeds_hash_for_grid(gridA, with_neighbors=True)
            
            fastest = math.inf
            route = None
            try:
                sg = self.sub_graph_dict[gridA]
                (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node2, node1, self.get_avg_speed_at_edge, G, time_window=10)
                if total_time < fastest:
                    fastest = total_time
                    route = avg_speed_route
            except nx.NetworkXNoPath:
    #             print("No path: {}-{}".format(node, b))
                pass
            except nx.NodeNotFound as e:
                utils.print_log("Error: {}".format(e))
    #         print(total_time, route)
    #         print(total_time, route)
            if route == None:
                return None, None
            return total_time, route
        
        elif node1 is not None and isinstance(gridA, int) and isinstance(gridB, str):
            # Single grid, just use node1 and gridA
            if DEBUG:
                print("Task D")

            # Assume that rsu_arr is present in the rsu
            G = self.get_speeds_hash_for_grid(gridB, with_neighbors=False)
            
            fastest = math.inf
            route = None
            try:
                sg = self.sub_graph_dict[gridB]
                (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node1, gridA, self.get_avg_speed_at_edge, G, time_window=10)
                if total_time < fastest:
                    fastest = total_time
                    route = avg_speed_route
            except nx.NetworkXNoPath:
    #             print("No path: {}-{}".format(node, b))
                pass
            except nx.NodeNotFound as e:
                utils.print_log("Error: {}".format(e))
    #         print(total_time, route)
            if route == None:
                return None, None
            return total_time, route
        else:
            print("Failed")
        pass

    def plot_grid_level_route(self, G, r):
        try:
            fig, ax = ox.plot_graph_route(G, r, node_size=0, node_zorder=1,
                                    axis_off=False, show=False, close=False, 
                                    fig_height=10, fig_width=10, dpi=300, margin=0.1,
                                    orig_dest_node_color='blue', route_color='black',
                                    route_alpha=1.0, orig_dest_node_alpha=0.8, use_geom=False)
            plt.grid(False)
            displayed_grids = []
            for r_ in r:
                node = nx_g.node[r_]
                if 'grid_id' in node:
                    grid_id = node['grid_id']
                    if grid_id not in displayed_grids:
            #                 print(grid_id)
                        for rsu in self.rsu_arr:
                            if grid_id == rsu.grid_id:
                                plt.plot(*rsu.poly.exterior.xy, color='red', alpha=0.5)
                                lng = rsu.poly.centroid.x
                                lat = rsu.poly.centroid.y
                                i = rsu.get_idx()
                                plt.text(lng - 0.02, lat + 0.005, grid_id)
                                displayed_grids.append(grid_id)

            return fig, ax
        
        except AttributeError as error:
            return None, None

    def get_coords_from_node(self, G, n):
        return (G.node[n]['x'], G.node[n]['y'])
