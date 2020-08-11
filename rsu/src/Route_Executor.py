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
import networkx as nx
import osmnx as ox
import geohash_hilbert as ghh
from os import listdir
from os.path import isfile, join

from src.conf import LOCAL_RSU_VARS
import common.src.adjustable_RSU as ag
import common.src.basic_utils as utils
import common.src.utility as geo_utils
import common.src.graph_breakdown as gb
from common.conf import GLOBAL_VARS

DEBUG = False

#WORKER number
RSU_ID = os.getenv(GLOBAL_VARS.RSU_ID)

#GHH generated
GRID_ID = GLOBAL_VARS.RSUS[RSU_ID]

class Route_Executor():
    def __init__(self, x, y):
        if not os.path.exists(os.path.join(os.getcwd(), 'data')):
            raise OSError("Must first download data, see README.md")
        self.data_dir = os.path.join(os.getcwd(), 'data')

        if not os.path.exists(os.path.join(self.data_dir, 'sub_graphs')):
            os.mkdir(os.path.join(self.data_dir, 'sub_graphs'))
        sub_graphs_dir = os.path.join(self.data_dir, 'sub_graphs')

        if not os.path.exists(os.path.join(self.data_dir, 'historical_speeds')):
            os.mkdir(os.path.join(self.data_dir, 'historical_speeds'))
        self.historical_speeds_dir = os.path.join(self.data_dir, 'historical_speeds')

        # DICTIONARIES
        if not os.path.exists(os.path.join(self.data_dir, 'avg_speeds')):
            os.mkdir(os.path.join(self.data_dir, 'avg_speeds'))
        self.avg_speeds_dir = os.path.join(self.data_dir, 'avg_speeds')

        # print(sub_graphs_dir)
        self.sub_graph_dict = geo_utils.read_saved_sub_graphs(sub_graphs_dir)
        # print(self.sub_graph_dict)

        target_area = LOCAL_RSU_VARS.EXTENDED_DOWNTOWN_NASH_POLY
        # Polys are just the larger boundaries to be used to "decrease" the number since we still use geohashing and it is still limited.
        polys = gb.divide_grid(target_area, (x, y))

        # NOTE: Only needed by some functions, maybe better to move?!
        self.rsu_arr = []
        for i in range(x):
            for j in range(y):
                idx = j + (i * y)
                p = polys[idx]
                gid = ghh.encode(p.centroid.x, p.centroid.y, precision=6)
                r = ag.adjustable_RSU(gid, p, (i, j))
                r.set_max_size(x, y)
                self.rsu_arr.append(r)

        file_path = os.path.join(self.data_dir, '{}-{}-G.pkl'.format(x, y))
        with open(file_path, 'rb') as handle:
            self.whole_graph = pickle.load(handle)
        # print("Whole graph: ", len(self.whole_graph.nodes))
        # Find what are the things needed to perform the route execution

        self._mongodb = None


    def assign_mongodb(self, mongodb):
        self._mongodb = mongodb

    def find_route(self, task):
        # print("Find_route of task: ", task['_id'])
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
            if DEBUG:
                print("{}-node1: {}, gridA: {}, gridB: {}, node2: None, time: {}".
                    format(task_count, n, gA, gB, t))
        elif next_node:
            r = self.get_task_route(node1=n, gridA=gA, gridB=gB, node2=next_node, time=t)
            if DEBUG:
                print("{}-node1: {}, gridA: {}, gridB: {}, node2: {}, time: {}".
                    format(task_count, n, gA, gB, next_node, t))
        # print(r)
        return r

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
        
    def get_shortest_route(self, sg, grid, node, time, bounds_list):
        # Assume that rsu_arr is present in the rsu
        # G = self.get_dataframe_historical_data(grid, with_neighbors=True)
        G = self.get_speeds_hash_for_grid(grid, with_neighbors=True)
        fastest = math.inf
        route = None
        for b in bounds_list:
            try:
                # (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node, b, self.get_travel_time_from_database, G, time_window=time)
                # (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node, b, self.get_avg_speed_at_edge, G, time_window=time)
                (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node, b, self.get_avg_speed_at_edge_dynamic, G, time_window=time)
                if total_time < fastest:
                    fastest = total_time
                    route = avg_speed_route
            except nx.NetworkXNoPath:
                print("No path: {}-{}".format(node, b))
                pass
            except nx.NodeNotFound as e:
                utils.print_log("Error: {}".format(e))

        if route == None:
            return None, None
        return (total_time, route)

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
            (total_time, route) = self.get_shortest_route(self.whole_graph, gridA, node1, time, bounds)
            return total_time, route
            
        elif node1 is None and (gridA is not None and isinstance(gridB, str)) and (gridB is not None and isinstance(gridB, str)):
            # Middle hop: must make use of node2 (the result of the previous hop)
            if DEBUG:
                print("Task B")
            bounds = self.get_bounds_between_two_grids(gridA, gridB)
            (total_time, route) = self.get_shortest_route(self.whole_graph, gridA, node2, time, bounds)
            return total_time, route
        
        elif node1 is not None and gridA is not None and gridB is None:
            # Last hop: must make use of node2 (the result of the previous hop)

            if DEBUG:
                print("Task C")
            
            # Assume that rsu_arr is present in the rsu
            # G = self.get_dataframe_historical_data(gridA, with_neighbors=True)
            G = self.get_speeds_hash_for_grid(gridA, with_neighbors=True)
            
            fastest = math.inf
            route = None
            try:
                sg = self.whole_graph
                # (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node2, node1, self.get_travel_time_from_database, G, time_window=time)
                # (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node2, node1, self.get_avg_speed_at_edge, G, time_window=time)
                (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node2, node1, self.get_avg_speed_at_edge_dynamic, G, time_window=time)
                if total_time < fastest:
                    fastest = total_time
                    route = avg_speed_route
            except nx.NetworkXNoPath:
                print("No path: {}-{}".format(node2, node1))
            except nx.NodeNotFound as e:
                utils.print_log("Error: {}".format(e))

            if route == None:
                return None, None
            return total_time, route
        
        elif node1 is not None and isinstance(gridA, int) and isinstance(gridB, str):
            # Single grid, just use node1 and gridA
            if DEBUG:
                print("Task D")

            # Assume that rsu_arr is present in the rsu
            # G = self.get_dataframe_historical_data(gridB, with_neighbors=True)
            G = self.get_speeds_hash_for_grid(gridB, with_neighbors=True)
            
            fastest = math.inf
            route = None
            try:
                sg = self.whole_graph
                # (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node1, gridA, self.get_travel_time_from_database, G, time_window=time)
                # (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node1, gridA, self.get_avg_speed_at_edge, G, time_window=time)
                (total_time, avg_speed_route) = nx.dijkstra_path_timed(sg, node1, gridA, self.get_avg_speed_at_edge_dynamic, G, time_window=time)
                

                if total_time < fastest:
                    fastest = total_time
                    route = avg_speed_route
            except nx.NetworkXNoPath:
                print("No path: {}-{}".format(node1, gridA))
            except nx.NodeNotFound as e:
                utils.print_log("Error: {}".format(e))
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

    def get_dataframe_historical_data(self, grid, with_neighbors=True):
        print("get_dataframe_historical_data({})".format(grid))
        if with_neighbors and self.rsu_arr:
            r = geo_utils.get_rsu_by_grid_id(self.rsu_arr, grid)
            d = r.get_neighbors(self.rsu_arr)
            
            hist_dfs = []
            for _, n in d.items():
                if n:
                    if n.grid_id != GRID_ID:
                        # print("Must get old data for {}".format(n.grid_id))
                        name = "{}_historical_speeds.pkl".format(n.grid_id)
                        hist_df = self.get_pickled_df(self.historical_speeds_dir, name)
                        hist_dfs.append(hist_df)

            all_hist_dfs = pd.concat(hist_dfs, ignore_index=True)

        return all_hist_dfs

    def get_pickled_df(self, dir, name):
        file_path = os.path.join(dir, name)
        return pd.read_pickle(file_path)

    # Get local actual data from mongodb while getting historical data from dataframe or dictionary
    def get_travel_time_from_database(self, start, end, attr, sensor_data=None, time_window=None):

        # Check first in the "real_data" key for the tmc_id
        # real_data = sensor_data['real_data']
        # Check next in the "hist_data" for the tmc_id if not present in the real_data
        hist_data = sensor_data
        
        tmc_id = None
        length = None

        # See JOURNAL_localdata_generator notebook
        time_traversed = 10.791

        if 0 in attr:
            if 'tmc_id' in attr[0]:
                tmc_id = attr[0]['tmc_id']
            if 'length' in attr[0]:
                length = attr[0]['length']

        if 0 not in attr:
            key = random.choice(list(attr))
            tmc_id = attr[key]['tmc_id']
            length = attr[key]['length']
        
        # Check first real data for tmc_id
        if tmc_id and length:
            if tmc_id in hist_data['tmc_id'].unique():
                now = datetime.datetime.now()
                average_speed_at_time_window = hist_data.loc[(hist_data['hour'] == time_window) & \
                                                                (hist_data['tmc_id'] == tmc_id)]['mean_speed'].values[0]
                time_traversed = length / average_speed_at_time_window

                elapsed = datetime.datetime.now() - now
                print("get hist data() in {}s".format(elapsed))
                return time_traversed
            else:
                now = datetime.datetime.now()
                curr_minute = now.minute
                curr_hour = time_window

                floor = int(math.floor(curr_minute / 10.0)) * 10
                ceiling = int(math.ceil(curr_minute / 10.0)) * 10
                s_time = '{}:{}'.format(curr_hour, floor)
                e_time = '{}:{}'.format(curr_hour, ceiling)
                if '60' in e_time:
                    e_time = '{}:{}'.format(curr_hour + 1, '00')
                    
                collection = self._mongodb._db[GRID_ID]
                res = collection.aggregate([
                    {"$match":{
                        "tmc_id": tmc_id,
                        "hour": curr_hour,
                        "minute": {"$gte": floor, "$lt": ceiling}
                    }},
                    {"$group":{
                        "_id": "$tmc_id",
                        "speeds": {
                            "$avg": "$SU"
                        }
                    }}
                ])

                mean_speed = 0

                for r in res:
                    mean_speed = r['speeds']

                if mean_speed:
                    time_traversed = length / mean_speed

                elapsed = datetime.datetime.now() - now
                print("get actual data() in {}s".format(elapsed))

                return time_traversed

        if not tmc_id and not length:
            return time_traversed

    ######## USES DICTIONARIES AND HOUR DELAYS ONLY ########
    def get_avg_speed_at_edge_dynamic(self, start, end, attr, sensor_data=None, time_window=None):
        tmc_id = None
        length = None
        # See JOURNAL_localdata_generator notebook
        time_traversed = 10.791
        
        time_hour = int(time_window.split(":")[0])
        time_minute = int(time_window.split(":")[1])

        delay_time_hour, delay_time_mins = utils.get_delay_time(time_hour, time_minute, delay = GLOBAL_VARS.DELAY_FACTOR)

        if 0 not in attr:
            key = random.choice(list(attr))
            tmc_id = attr[key]['tmc_id']
            length = attr[key]['length']
        else:
            if 0 in attr:
                if 'tmc_id' in attr[0]:
                    tmc_id = attr[0]['tmc_id']
                if 'length' in attr[0]:
                    length = attr[0]['length']
        
        if tmc_id and tmc_id in sensor_data:
            parent_grid = GRID_ID
            for k, v in LOCAL_RSU_VARS.SUB_GRIDS.items():
                if GRID_ID in v:
                    parent_grid = k
            
            if tmc_id in LOCAL_RSU_VARS.TMC_DICT[parent_grid]:
                actual_hour = time_hour
                actual_min  = time_minute
                average_speed_at_time_window = sensor_data[tmc_id][actual_hour][actual_min]
            else:
                # Get the grid_id where this tmc_id is from
                for k, v in LOCAL_RSU_VARS.TMC_DICT.items():
                    if tmc_id in v:
                        other_rsu = k
                        break
                
                # Use manhattan distance as the delay
                r1 = geo_utils.get_rsu_by_grid_id(self.rsu_arr, parent_grid)
                r2 = geo_utils.get_rsu_by_grid_id(self.rsu_arr, other_rsu)
                delay = r1.get_manhattan_distance(r2)
        
                # TODO: Fix this hardcoded
                if GLOBAL_VARS.NEIGHBOR_LEVEL != 0:
                    delay_time_range = utils.get_range(0, delay_time_mins, granularity = GLOBAL_VARS.GRANULARITY)
                    # print(f"Delayed: {delay_time_range}, time: {time_window}, delayed_time: {delay_time_hour}:{delay_time_mins}")
                    vals = [sensor_data[tmc_id][delay_time_hour][minute] for minute in delay_time_range]
                else:
                    orig_time_range = utils.get_range(time_hour, time_minute, granularity = GLOBAL_VARS.GRANULARITY)
                    vals = [sensor_data[tmc_id][time_hour][minute] for minute in orig_time_range]
                average_speed_at_time_window = sum(vals) / len(vals)

            time_traversed = length / average_speed_at_time_window

        return time_traversed

    def get_avg_speed_at_edge(self, start, end, attr, sensor_data=None, time_window=None):
        tmc_id = None
        length = None
        # See JOURNAL_localdata_generator notebook
        time_traversed = 10.791
        
        if 0 not in attr:
            key = random.choice(list(attr))
            tmc_id = attr[key]['tmc_id']
            length = attr[key]['length']
        else:
            if 0 in attr:
                if 'tmc_id' in attr[0]:
                    tmc_id = attr[0]['tmc_id']
                if 'length' in attr[0]:
                    length = attr[0]['length']
        
        if tmc_id and tmc_id in sensor_data:
            # TODO: Check if tmc_id is within the local data
            # Give some delay if not the local, depends on distance from optimal rsu
            # For now just give a delay of 1 hour
            parent_grid = GRID_ID
            for k, v in LOCAL_RSU_VARS.SUB_GRIDS.items():
                if GRID_ID in v:
                    parent_grid = k
            
            if tmc_id in LOCAL_RSU_VARS.TMC_DICT[parent_grid]:
                actual_time_window = time_window
            else:
                # Get the grid_id where this tmc_id is from
                for k, v in LOCAL_RSU_VARS.TMC_DICT.items():
                    if tmc_id in v:
                        other_rsu = k
                        break
                
                # Use manhattan distance as the delay
                r1 = geo_utils.get_rsu_by_grid_id(self.rsu_arr, parent_grid)
                r2 = geo_utils.get_rsu_by_grid_id(self.rsu_arr, other_rsu)
                delay = r1.get_manhattan_distance(r2)
        
                # TODO: Fix this hardcoded
                if GLOBAL_VARS.NEIGHBOR_LEVEL == 0:
                    delay = 0
                actual_time_window = (time_window - delay) % 24

            average_speed_at_time_window = sensor_data[tmc_id]['speeds'][actual_time_window]
            time_traversed = length / average_speed_at_time_window

        return time_traversed

    def random_speeds(self, start, end, attr, sensor_data=None, time_window=None):
        if 0 not in attr:
            key = random.choice(list(attr))
            tmc_id = attr[key]['tmc_id']
        else:
            tmc_id = attr[0]['tmc_id']
        average_speed_at_time_window = random.uniform(1.86, 80.78)
        return average_speed_at_time_window

    # HACK: The with_neighbors is a work around because else it has no idea of others, or i should load all?
    # FIXME: Changed directory to accomodate other grid dimensions, but for now, hard coding 5x5
    # IDEA: Local should be more granular, but then i would need to change even the request/query to include more granularity in the time_window
    def get_speeds_hash_for_grid(self, grid_id, with_neighbors=False):
        G = {}
        file_path = os.path.join(self.avg_speeds_dir, f'one_minute/{grid_id}_dict_avg_speeds_minute.pkl')
        # file_path = os.path.join(self.avg_speeds_dir, '5x5/{}-avg_speeds.pkl'.format(grid_id))
        with open(file_path, 'rb') as handle:
            g = pickle.load(handle)
            G = {**G, **g}

        if with_neighbors and self.rsu_arr:
            r = geo_utils.get_rsu_by_grid_id(self.rsu_arr, grid_id)
            d = r.get_neighbors(self.rsu_arr)

            for _, n in d.items():
                if n:
                    file_path = os.path.join(self.avg_speeds_dir, f'one_minute/{n.grid_id}_dict_avg_speeds_minute.pkl')
                    # file_path = os.path.join(self.avg_speeds_dir, '5x5/{}-avg_speeds.pkl'.format(n.grid_id))
                    with open(file_path, 'rb') as handle:
                        g = pickle.load(handle)
                        G = {**G, **g}
        return G