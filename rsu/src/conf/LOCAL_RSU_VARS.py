from shapely.geometry import Polygon

LNG_EXTEND = 0.0054931640625 * 4
LAT_EXTEND = 0.00274658203125 * 4
EXTENDED_DOWNTOWN_NASH_POLY = Polygon([(-86.878722 - LNG_EXTEND, 36.249723 + LAT_EXTEND),
                              (-86.878722 - LNG_EXTEND, 36.107442 - LAT_EXTEND),
                              (-86.68081100000001 + LNG_EXTEND, 36.107442 - LAT_EXTEND),
                              (-86.68081100000001 + LNG_EXTEND, 36.249723 + LAT_EXTEND),
                              (-86.878722 - LNG_EXTEND, 36.249723 + LAT_EXTEND)])