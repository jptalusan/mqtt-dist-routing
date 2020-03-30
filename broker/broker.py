from common.src.mqtt_utils import MyMQTTClass
from common.src.mongo_class import MyMongoDBClass
from common.conf import GLOBAL_VARS
from src.Broker_Mqtt import Broker_Mqtt

#generate Rsu arr
import os
import pickle
import pandas as pd
import geohash_hilbert as ghh
import common.src.adjustable_RSU as ag
import common.src.basic_utils as utils
import common.src.utility as geo_utils
import common.src.graph_breakdown as gb

from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import MultiPoint

# http://www.steves-internet-guide.com/mqtt-clean-sessions-example/

# Generate rsu_arr
'''
Needs a lot of files:
1. {}-{}-grids_df.pkl
2. GLOBAL_VARS.EXTENDED_DOWNTOWN_NASH_POLY
'''
def divide_grid_temp(boundary, divisions):    
    wd, hd = divisions
    # Divide the boundary
    points = MultiPoint(boundary.boundary.coords)
    height = abs(points[2].y - points[1].y)
    hdivs = height / hd
    width = abs(points[1].x - points[0].x)
    wdivs = width / wd

    tl = Point(points[0].x, points[0].y)
    
    polys = []
    
    for i in range(wd):
        for j in range(hd):
            
            tl3 = Point(tl.x + (wdivs * i), tl.y - (hdivs * j))
            tr3 = Point(tl.x + (wdivs * (i + 1)), tl.y - (hdivs * j))
            bl3 = Point(tl.x + (wdivs * i), tl.y - (hdivs * (j + 1)))
            br3 = Point(tl.x + (wdivs * (i + 1)), tl.y - (hdivs * (j + 1)))
            pl3 = [tl3, tr3, br3, bl3]
            poly3 = Polygon([[p.x, p.y] for p in pl3])
            polys.append(poly3)
    return polys

def generate_RSU_arr(x, y):
    target_area = GLOBAL_VARS.EXTENDED_DOWNTOWN_NASH_POLY
    # Polys are just the larger boundaries to be used to "decrease" the number since we still use geohashing and it is still limited.
    polys = gb.divide_grid(target_area, (x, y))
    rsu_arr = []
    for i in range(x):
        for j in range(y):
            idx = j + (i * y)
            p = polys[idx]
            gid = ghh.encode(p.centroid.x, p.centroid.y, precision=6)
            r = ag.adjustable_RSU(gid, p, (i, j))
            r.set_max_size(x, y)
            rsu_arr.append(r)

    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        raise OSError("Must first download data, see README.md")
    data_dir = os.path.join(os.getcwd(), 'data')

    file_path = os.path.join(data_dir, '{}-{}-grids_df.pkl'.format(x, y))
    with open(file_path, 'rb') as handle:
        df = pd.read_pickle(handle)

    sub_grid_rsus = []
    TMC_THRESH = df['tmc_count'].quantile(0.75)
    DIV_X, DIV_Y = 2, 2
    for i, row in df.iterrows():
        gid = row['grid_id']
        tmc_count = row['tmc_count']
        if tmc_count > TMC_THRESH:
            # BUG: If DIV_X and DIV_Y are odd, the central grid has the same gid as the parent grid
    #         if tmc_count / (DIV_X * DIV_Y) > TMC_THRESH:
    #             DIV_X, DIV_Y = 3, 3
                
            r = geo_utils.get_rsu_by_grid_id(rsu_arr, gid)
            r_poly = r.poly
            sub_polys = divide_grid_temp(r_poly, (DIV_X, DIV_Y))
            
            for p in sub_polys:
                new_gid = ghh.encode(p.centroid.x, p.centroid.y, precision=6)
                new_r = ag.adjustable_RSU(new_gid, p, (1000, 1000))
                new_r.queue_limit = GLOBAL_VARS.QUEUE_THRESHOLD
                new_r.set_max_size(x, y)
                sub_grid_rsus.append(new_r)
                # print("Adding: {}".format(new_gid))
                r.add_sub_grid(new_r)

    # main_no_sub_polys = [r.poly for r in rsu_arr if not r.get_sub_grids()]
    # sub_grid_polys = [r.poly for r in sub_grid_rsus]

    # SUB_GRIDS_DICT = {}
    # for r in rsu_arr:
    #     if r.get_sub_grids():
    #         SUB_GRIDS_DICT[r.grid_id] = [sg.grid_id for sg in r.get_sub_grids()]

    file_path = os.path.join(data_dir, "{}-{}-rsu_arr.pkl".format(x, y))
    with open(file_path, 'wb') as handle:
        pickle.dump(rsu_arr, handle)

    utils.print_log("Generated rsu_arr for broker.")

if __name__ == "__main__":
    generate_RSU_arr(5, 5)

    mongodbc = MyMongoDBClass(host="mongo", db="admin")
    mongodbc.get_client().is_mongos

    if __debug__ == 1:
        mongodbc.delete_all(GLOBAL_VARS.TASKS)
        mongodbc.delete_all(GLOBAL_VARS.QUERIES)

    mqttc = Broker_Mqtt(host="mqtt", mongodb_c=mongodbc)
    mqttc.connect()
    mqttc.start_sub_thread([GLOBAL_VARS.QUERY_TO_BROKER, 
                            GLOBAL_VARS.SUB_RESPONSE_TO_BROKER, 
                            GLOBAL_VARS.PROCESSED_TO_BROKER,
                            GLOBAL_VARS.SIMULATED_QUERY_TO_BROKER,
                            GLOBAL_VARS.ALLOCATION_STATUS_TO_BROKER])