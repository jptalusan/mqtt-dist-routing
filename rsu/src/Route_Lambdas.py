import pickle
import os
import random
import pandas as pd
import datetime
import math
import numpy as np

import common.src.utility as geo_utils
from common.conf import GLOBAL_VARS
import common.src.basic_utils as utils

#WORKER number
RSU_ID = os.getenv(GLOBAL_VARS.RSU_ID)

#GHH generated
GRID_ID = GLOBAL_VARS.RSUS[RSU_ID]

def get_speeds_hash_for_grid(grid, rsu_arr, with_neighbors=True):
    # utils.print_log("get_speeds_hash_for_grid({})".format(grid))
    # print("RSU_ID:", RSU_ID, "GRID_ID:", GRID_ID)

    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        raise OSError("Must first download data, see README.md")
    data_dir = os.path.join(os.getcwd(), 'data')

    if not os.path.exists(os.path.join(data_dir, 'actual_speeds')):
        os.mkdir(os.path.join(data_dir, 'actual_speeds'))
    actual_speeds_dir = os.path.join(data_dir, 'actual_speeds')

    if not os.path.exists(os.path.join(data_dir, 'historical_speeds')):
        os.mkdir(os.path.join(data_dir, 'historical_speeds'))
    historical_speeds_dir = os.path.join(data_dir, 'historical_speeds')

    if with_neighbors and rsu_arr:
        r = geo_utils.get_rsu_by_grid_id(rsu_arr, grid)
        d = r.get_neighbors(rsu_arr)

        if grid == GRID_ID:
            # print("Central grid is the local grid {}".format(GRID_ID))
            name = "{}_actual_speeds.pkl".format(grid)
            local_df = get_pickled_df(actual_speeds_dir, name)
            # print(local_df.head())
        
        hist_dfs = []
        for _, n in d.items():
            if n:
                if n.grid_id == GRID_ID:
                    # print("This is local grid {}".format(GRID_ID))
                    name = "{}_actual_speeds.pkl".format(n.grid_id)
                    local_df = get_pickled_df(actual_speeds_dir, name)
                    # print(local_df.head())
                else:
                    # print("Must get old data for {}".format(n.grid_id))
                    name = "{}_historical_speeds.pkl".format(n.grid_id)
                    hist_df = get_pickled_df(historical_speeds_dir, name)
                    # print(hist_df.head())
                    # print(hist_df.shape)
                    hist_dfs.append(hist_df)

        all_hist_dfs = pd.concat(hist_dfs, ignore_index=True)
        # print(all_hist_dfs)
        # print(all_hist_dfs.shape)

    return {"real_data": local_df, "hist_data": all_hist_dfs}

def get_pickled_df(dir, name):
    file_path = os.path.join(dir, name)
    return pd.read_pickle(file_path)

def get_travel_time(start, end, attr, sensor_data=None, time_window=None):
    # Check first in the "real_data" key for the tmc_id
    real_data = sensor_data['real_data']
    # Check next in the "hist_data" for the tmc_id if not present in the real_data
    hist_data = sensor_data['hist_data']
    
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
            # print("Found in old data")
            average_speed_at_time_window = hist_data.loc[(hist_data['hour'] == time_window) & \
                                                            (hist_data['tmc_id'] == tmc_id)]['mean_speed'].values[0]
            time_traversed = length / average_speed_at_time_window
            return time_traversed
        elif tmc_id in real_data['tmc_id'].unique():
            now = datetime.datetime.now()
            curr_minute = now.minute
            curr_hour = now.hour

            floor = int(math.floor(curr_minute / 10.0)) * 10
            ceiling = int(math.ceil(curr_minute / 10.0)) * 10
            s_time = '{}:{}'.format(curr_hour, floor)
            e_time = '{}:{}'.format(curr_hour, ceiling)
            if '60' in e_time:
                e_time = '{}:{}'.format(curr_hour + 1, '00')
                
            # print("Found in real data")
            real_data = real_data.loc[real_data['tmc_id'] == tmc_id].between_time(s_time, e_time)
            mean_speed = real_data.mean(axis=0).values[0]
            if np.isnan(mean_speed):
                mean_speed = 27.3121
            time_traversed = length / mean_speed
            return time_traversed

    if not tmc_id and not length:
        return time_traversed

def random_speeds(start, end, attr, sensor_data=None, time_window=None):
    average_speed_at_time_window = random.uniform(1, 100)
    return average_speed_at_time_window

# TODO: Check how different/slow the dataframe vs dict is?
def get_travel_time_using_dictionaries():
    pass