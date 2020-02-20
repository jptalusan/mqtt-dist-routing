import pandas as pd
import numpy as np
import networkx as nx
import osmnx as ox
import math
import random
import geohash_hilbert as ghh
import datetime
import time
from sklearn.metrics import explained_variance_score
from shapely.geometry import Point

from .utility import *

current_milli_time = lambda: int(round(time.time() * 1000))

# A query handles a group of tasks
# Maybe only applicable in centralized, else need to query the databases i said below.
class Query(object):
    def __init__(self):
        pass

# Probably need a database for this
class Task(object):
    
    inquiry_time = None
    assignment_time = None # Issue time
    execution_start_time = None
    execution_end_time = None
    actual_grid_assignment = None
    manhattan_distance = None
    
    def __init__(self, t_list):
        self.inquiry_time = current_milli_time()
        self._id = t_list[0]
        self.node = t_list[1]
        self.gridA = t_list[2]
        self.gridB = t_list[3]
        self.time_window = t_list[4]
        
        pass
    
    def get_tuple(self):
        pass
    
    # How long it lives in the queue before processing
    def assign_task(self, actual_grid_assignment):
        self.assignment_time = current_milli_time()
        self.actual_grid_assignment = actual_grid_assignment
        pass
    
    # Does this really belong here?
    # I think this is ok, but should be called by the RSU
    def start_execution(self):
        self.execution_start_time = current_milli_time()
        
        r1 = get_rsu_by_grid_id(rsu_arr, self.actual_grid_assignment)
        r2 = get_rsu_by_grid_id(rsu_arr, self.start_point)
        self.manhattan_distance = manhattan_distance(r1, r2)
        pass
    
    def end_execution(self):
        self.execution_end_time = current_milli_time()
        elapsed = self.execution_end_time - self.execution_start_time
        return elapsed
    
    # Actual, links, time_window, time stats (exec, issue etc..)
    def get_stats(self):
        pass
        
    def __repr__(self):
        return "{:16.16}\t{}:{}\\{}\t{}".format(self._id, self.node, self.gridA, self.gridB, self.time_window)

    def __str__(self):
        return "{:16.16}\t{}:{}\\{}\t{}".format(self._id, self.node, self.gridA, self.gridB, self.time_window)