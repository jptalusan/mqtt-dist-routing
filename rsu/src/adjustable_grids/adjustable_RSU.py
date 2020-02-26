from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Polygon
from shapely.ops import nearest_points

from sklearn.metrics import explained_variance_score
import random
import math
import datetime
import time
import numpy as np
'''
Between Raspberry Pi nodes:
100 packets transmitted, 100 received, 0% packet loss, time 1009ms
rtt min/avg/max/mdev = 0.625/0.751/0.857/0.042 ms

pi@pi3-08:~$ traceroute google.com
traceroute to google.com (172.217.31.142), 30 hops max, 60 byte packets
 1  fi-isa4.naist.jp (163.221.68.1)  1.441 ms  1.276 ms  1.190 ms
 2  juniper-core1-v824.naist.jp (163.221.6.97)  0.502 ms  0.424 ms  0.347 ms
 3  juniper-itc1-v830.naist.jp (163.221.6.122)  0.483 ms  0.406 ms  0.487 ms
 4  wnoc-juniper5-v309.naist.jp (163.221.1.38)  0.408 ms  0.535 ms  0.458 ms
 5  ve-7.juniper1.dojima.wide.ad.jp (203.178.136.170)  2.519 ms  2.445 ms  2.361 ms
 6  ve-3761.juniper1.notemachi.wide.ad.jp (203.178.136.109)  8.970 ms  9.447 ms  9.352 ms
 7  ve-51.nexus1.otemachi.wide.ad.jp (203.178.141.141)  8.338 ms  8.566 ms  8.515 ms
 8  ve-5.alaxala1.otemachi.wide.ad.jp (203.178.140.194)  9.800 ms  12.800 ms  14.757 ms
 9  as15169.dix-ie.jp (202.249.2.189)  8.516 ms  8.443 ms  8.370 ms
10  108.170.242.161 (108.170.242.161)  8.612 ms  8.661 ms  8.523 ms
11  74.125.251.235 (74.125.251.235)  9.626 ms 74.125.251.237 (74.125.251.237)  9.506 ms  9.426 ms
12  nrt20s08-in-f14.1e100.net (172.217.31.142)  8.576 ms  8.459 ms  8.574 ms

'''
class simulator(object):
    
    hops_to_ms = 2.445 #ms
    rsu_to_rsu = 11000 #KB/s 
    
    graph_data_df = None
    speed_data_df = None
    
    def __init__(self):
        pass
    
    # TODO: Stub because using real data takes too long, i will need to pickle it in the future.
    def generate(self, x, dist):
        manhattan_distance = dist
        factor = 0.12 * manhattan_distance
        loc = 1.1 + (factor)
        ploc = random.uniform(-1 * manhattan_distance, manhattan_distance)
        Y=np.random.normal(loc * x, factor)
        return Y
    
    def get_manhattan_stub(self, r1, r2):
        distance_between_pts = Point(a[1], a[0]).distance(Point(b[1], b[0]))
        return round(distance_between_pts * 100)
        
    def get_data_accuracy_stub(self):
        x = np.linspace(1, 100)
        optimal_md = self.get_manhattan_stub(self.step_optimal_grid)
        EVS = explained_variance_score(np.sin(x), self.generate(np.sin(x), optimal_md))
        return EVS
    
    def get_processing_delay(self):
        pass
    
    def get_communication_delay(self):
        pass
    
    # Probably the actual location so can easily query when needed
    def set_speed_data_dir(self, speeds_dir, ext):
        nameList = os.listdir(graphs_dir)
        extension = ext
        names = []
        sizes = []
        data = {}
        for n in nameList:
            if extension in n:
                path = os.path.join(sub_graphs_dir, n)
                size = os.stat(path).st_size
                names.append(n[5:-4])
                sizes.append(size)

        data['names'] = names
        data['sizes'] = sizes

        df = pd.DataFrame(data)
        self.graph_data_df = df
        pass
    
    def set_graph_data_dir(self, graphs_dir, ext):
        nameList = os.listdir(graphs_dir)
        extension = ext
        names = []
        sizes = []
        data = {}
        for n in nameList:
            if extension in n:
                path = os.path.join(sub_graphs_dir, n)
                size = os.stat(path).st_size
                names.append(n[5:-4])
                sizes.append(size)

        data['names'] = names
        data['sizes'] = sizes

        df = pd.DataFrame(data)
        self.graph_data_df = df
    
    
class adjustable_RSU(object):
    
    # Class variables?
    queue = []
    queue_limit = 0
    
    curr_delay = 0.0
    curr_px = 0.0
    curr_accuracies = []
    
#     delay_threshold = 0
#     model_accuracy = 0
#     px_threshold = 0
    subgraph = None
#     identity = ''
    dataset = None
    

    # Coords are x, y and not row, col.
    def __init__(self, grid_id, poly, coords):
        self.coords = coords
        self.grid_id = grid_id
        self.poly = poly
        
        self.queue = []
        self.curr_accuracies = []
        self.curr_delay = 0.0
        self.curr_px = 0.0
        
    
    def load_with_data(self, subgraph=None, dataset=None):
        if subgraph:
            self.subgraph = subgraph
        if dataset:
            self.dataset = dataset
            
    def add_task(self, task, force=False, constraint='delay'):
        # TODO: Use the simulator class to answer these values.
        task_px = task.calculate_total_px_time()
        
        # Affected by change in actual grid
        task_accuracy = task.get_data_accuracy_stub()
        
        # Not affected by change in actual grid
        optm_g, next_g = task.get_optimal_and_next_grids()
        task_delay = task.get_communication_delay(optm_g, next_g)
        
        if force:
#             self.curr_px += task_px
#             self.curr_accuracies.append(task_accuracy)
#             self.curr_delay += task_delay
            self.queue.append(task)
            return True
        
        # constraints
        met_px_constraint    = False
        met_model_constraint = False
        met_delay_constraint = False
        met_queue_constraint = False
        
        use_px_constraint = False
        use_acc_constraint = False
        use_delay_constraint = False
        use_queue_constraint = False
        
        constraints = constraint.split("|")
        if 'px' in constraints:
            use_px_constraint = True
        if 'acc' in constraints:
            use_acc_constraint = True
        if 'delay' in constraints:
            use_delay_constraint = True
        if 'queue' in constraints:
            use_queue_constraint = True
            
        if use_px_constraint:
            processing = self.curr_px + task_px
            if processing <= self.px_threshold:
                met_px_constraint = True
        else:
            met_px_constraint = True
        
        if use_acc_constraint:
            if task_accuracy >= self.model_accuracy:
                met_model_constraint = True
        else:
            met_model_constraint = True
        
        if use_delay_constraint:
            delay = self.curr_delay + task_delay
            if delay <= self.delay_threshold:
                met_delay_constraint = True
        else:
            met_delay_constraint = True
        
        if use_queue_constraint:
            if len(self.queue) < self.queue_limit:
                met_queue_constraint = True
        else:
            met_queue_constraint = True

        if met_px_constraint and \
           met_model_constraint and \
           met_delay_constraint and \
           met_queue_constraint:
            if DEBUG == 1:
                print("{} Adding task: {}-{}".format(self.identity, task.step_count, task.task_id))
            self.queue.append(task)
            
            self.curr_px += task_px
            self.curr_accuracies.append(task_accuracy)
            self.curr_delay += task_delay
#             print("Success: {}".format(self))
            return True
        else:
            return False

#     def __iter__(self):
#         return self
#     def __next__(self):
#         self.idx += 1
#         try:
#             return self.data[self.idx-1]
#         except IndexError:
#             self.idx = 0
#             raise StopIteration  # Done iterating.

    def get_neighbors(self, rsu_arr):
        x, y = self.coords[0], self.coords[1]
        north = self.get_idx(x, y - 1)
        if north is None:
            north = None
        else:
            north = rsu_arr[north]
            
        south = self.get_idx(x, y + 1)
        if south is None:
            south = None
        else:
            south = rsu_arr[south]
            
        east = self.get_idx(x + 1, y)
        if east is None:
            east = None
        else:
            east = rsu_arr[east]
        
        west = self.get_idx(x - 1, y)
        if west is None:
            west = None
        else:
            west = rsu_arr[west]
            
        north_east = self.get_idx(x + 1, y - 1)
        if north_east is None:
            north_east = None
        else:
            north_east = rsu_arr[north_east]
            
        north_west = self.get_idx(x - 1, y - 1)
        if north_west is None:
            north_west = None
        else:
            north_west = rsu_arr[north_west]
            
        south_east = self.get_idx(x + 1, y + 1)
        if south_east is None:
            south_east = None
        else:
            south_east = rsu_arr[south_east]
            
        south_west = self.get_idx(x - 1, y + 1)
        if south_west is None:
            south_west = None
        else:
            south_west = rsu_arr[south_west]
            
        return { 'north'     : north,
                 'south'     : south,
                 'east'      : east,
                 'west'      : west,
                 'north-east': north_east,
                 'north-west': north_west,
                 'south-east': south_east,
                 'south-west': south_west
        }
        
    def graph_neighbors(self, rsu_arr):
        d = self.get_neighbors(rsu_arr)
        
        fig, ax = plt.subplots(1, 1, figsize=(5, 5))
        
        for k, v in d.items():
            if v is not None:
                plt.plot(*v.poly.exterior.xy, color='red', alpha=1)
                plt.fill(*v.poly.exterior.xy, color='red', alpha=0.2)
                plt.text(v.poly.centroid.x, v.poly.centroid.y, str(v.get_idx()) + ':' +  str(v.grid_id), fontsize=8)
        return fig
        
    def get_idx(self, x = None, y = None):
        if x is not None and y is not None:
            if x >= self.MAX_X or y >= self.MAX_Y:
                return None
            
            if x < 0 or y < 0:
                return None
            r = y + (x * self.MAX_Y)
            return r
        
        return self.coords[1] + (self.coords[0] * self.MAX_Y)
    
    def set_max_size(self, X, Y):
        self.MAX_X = X
        self.MAX_Y = Y
        
    def __repr__(self):
        return str({'grid_id':self.grid_id, 'coords':self.coords, 'idx': self.get_idx()})
    def __str__(self):
        return 'RSU(grid_id=' + str(self.grid_id) + ', coords=' + str(self.coords) + ', idx=' + str(self.get_idx()) + ')'
    
    
    # Methods that deal with task allocationm
    