from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Polygon
from shapely.ops import nearest_points

import random
import math
import datetime
import time
import numpy as np
   
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
    