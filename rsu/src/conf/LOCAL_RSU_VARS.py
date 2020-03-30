from shapely.geometry import Polygon
import os
import pickle

LNG_EXTEND = 0.0054931640625 * 4
LAT_EXTEND = 0.00274658203125 * 4
EXTENDED_DOWNTOWN_NASH_POLY = Polygon([(-86.878722 - LNG_EXTEND, 36.249723 + LAT_EXTEND),
                              (-86.878722 - LNG_EXTEND, 36.107442 - LAT_EXTEND),
                              (-86.68081100000001 + LNG_EXTEND, 36.107442 - LAT_EXTEND),
                              (-86.68081100000001 + LNG_EXTEND, 36.249723 + LAT_EXTEND),
                              (-86.878722 - LNG_EXTEND, 36.249723 + LAT_EXTEND)])

SUB_GRIDS = {'SPBZuN': ['SPBQ4@', 'SPBQvA', 'SPBZs6', 'SPBZ77'],
             'SPB_r0': ['SPB_pP', 'SPB_uP', 'SPB_nt', 'SPB_wt'],
             'SPBZYd': ['SPBZWF', 'SPBZTl', 'SPBZbn', 'SPBZNH'],
             'SPBY71': ['SPBY5O', 'SPBY@O', 'SPBY3s', 'SPBYBs'],
             'SPEOxP': ['SPEOzp', 'SPEOkp', 'SPEOv@', 'SPEOoV'],
             'SPBbQt': ['SPBbOU', 'SPBbaT', 'SPBbSV', 'SPBbX9']}

file_path = os.path.join('data/tmc_dict.pkl')
with open(file_path, 'rb') as handle:
    TMC_DICT = pickle.load(handle)