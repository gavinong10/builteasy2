import geopandas as gpd
from shapely.geometry import Point, LineString
import geopy.distance
import pandas as pd
import datetime
import threading

import argparse
from multiprocessing import Pool

import errno    
import os

#BRISBANE_POINT=Point(153.025100, -27.469515)
BRISBANE_COORDS=(153.025100, -27.469515)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def return_pairs(coords):
    pairs = []
    i = 1
    for i in range(len(coords)):
        pairs.append((coords[i-1], coords[i]))
        i += 1
    return pairs

def get_coords_from_point(point):
    return (point.xy[0][0], point.xy[1][0])

class DistFilterThread (threading.Thread):
   def __init__(self, threadID, name, i, data, batch_size, distance_km, point):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.i = i
      self.data = data
      self.batch_size = batch_size
      self.batch_data = data[i * batch_size: (i+1) * batch_size]
      self.distance_km = distance_km
      self.point = point
      self.batch_res = None
      
   def run(self):
      self.batch_res = self.batch_data[self.batch_data.geometry.apply(lambda x: geopy.distance.vincenty(get_coords_from_point(x.centroid), get_coords_from_point(self.point)).km, convert_dtype=True) <= self.distance_km]
      return self.batch_res

def filter_by_area(data, min_area_m2=700, max_area_m2=1200):
    area = data.geometry.area * 1e10
    return data[(area >= min_area_m2) & (area <= max_area_m2)]

def get_by_lot(data, plan, lot):
    # Might return more than one entry
    # plan = unicode(plan)
    lot = unicode(lot)
    entry = data[(data["PLAN"] == plan) & (data["LOT"] == lot)]
    return entry

def is_corner_lot(data, index, dist_val):
    #Algorithm 1
    # Create a marked list '0' of all the lines of a boundary.
    # Get a random line boundary
    # Extend on that line until there is 22.5 degrees of variation max between the lines
    # Mark all these lines as 'seen' and ensure that length meets a certain threshold
    # Move along adjacent lines until a length is met above a min distance
    # Check angle is >75 degrees between the longest line between the marked section and the new section.

    #Algorithm 2
    # Get the centroid of the property and draw a line to the nearest section of the longest boundary line
    # Minimum bounding?
    # Draw lines in 90 degree increments between these points
    # As you rotate these 4 lines, if two lines are subsequently untouched, this is a corner lot.

    # Algorithm 3
    geom = data.loc[index]['geometry']

    # Extract the centroids and lengths of each side
    corner_coords = zip(*geom.minimum_rotated_rectangle.exterior.xy)
    side_objs = [{"pair": pair, "orig_line": LineString(pair)} for pair in return_pairs(corner_coords)]
    for side_obj in side_objs:
        #side_obj["length_m"] = geopy.distance.vincenty(side_obj["pair"][0], side_obj["pair"][1]).m
        side_obj["centroid"] = side_obj["orig_line"].centroid
        # Generate a set of lengths that is 50% in length
        side_obj["trunc_line"] = LineString((Point(((pair[0][0] + side_obj["centroid"].xy[0][0]) * 0.5, (pair[0][1] + side_obj["centroid"].xy[1][0]) * 0.5)), Point(((pair[1][0]  + side_obj["centroid"].xy[0][0]) * 0.5, (pair[1][1] + side_obj["centroid"].xy[1][0]) * 0.5))))
    # # If >= 2 sides do NOT intersect, then it is a corner lotsl
    candidate_geoms = data.cx[geom.bounds[0]-dist_val:geom.bounds[2]+dist_val, geom.bounds[1]-dist_val: geom.bounds[3]+dist_val].geometry
    num_adjacent = 0
    for side_obj in side_objs:
        num_adjacent += (candidate_geoms.intersects(side_obj['trunc_line']).sum() > 1)
        if num_adjacent >= 2:
            return False
    
    return True

def CornerLotIdentifyThreading(i, mapfile, batch_size, dist_val):
    if (i+2) * batch_size > (len(mapfile) - 1):
        end = len(mapfile) - 1
    else:
        end = min((i+1) * batch_size, len(mapfile) - 1)
    thread_indices = mapfile.iloc[i * batch_size: (i+1) * batch_size].index
    return thread_indices.to_series().apply(lambda x: is_corner_lot(mapfile, x, dist_val) )

def pcorner(i):
    return CornerLotIdentifyThreading(*i)

def filter_by_plan(data):
    return data[data["PLAN"].str.startswith("SP") | data["PLAN"].str.startswith("RP")]

def filter_by_regularity(data, factor=0.8):
    regularity = data.geometry.apply(lambda x: x.area / x.minimum_rotated_rectangle.area)
    return data[regularity > factor]

def main():
    pass

if __name__ == "__main__":
    
    #sys.argv = ['', '--mapfile', 'data/truncated/boundaries_shp/Property_boundaries___DCDB_Lite.shp', '--searchwindow', '153.0548787','-27.3607943','153.105812','-27.396514', '--nthreads', '3']
    #sys.argv = ['', '--mapfile', 'data/boundaries_shp/Property_boundaries___DCDB_Lite.shp',  '--searchwindow', '153.0548787','-27.3607943','153.105812','-27.396514', '--nthreads', '3']
    parser = argparse.ArgumentParser(description='Process arguments to the data analyzer.')
    parser.add_argument('--mapfile', 
                        metavar='file path', 
                        type=str, 
                        nargs='?',
                        default="data/boundaries_gdb/data.gdb",
                        help='The path to the mapfile data')

    parser.add_argument('--adjacentwidth', 
                        metavar='degree', 
                        type=float, 
                        nargs='?',
                        default=0.002,
                        help='The degrees to search around a property')

    parser.add_argument('--finalizefilterfactor', 
                        metavar='factor', 
                        type=float, 
                        nargs='?',
                        default=0.9,
                        help='The factor to reduce the result by to cut off the edge')

    parser.add_argument('--searchwindow', 
                        metavar=('long1', 'lat1', 'long2', 'lat2'), 
                        type=float, 
                        nargs=4,
                        default=(153.0548787,-27.3607943,153.105812,-27.396514),
                        help='The window to search for properties')

    parser.add_argument('--outputfilepath', 
                        metavar=('file path',), 
                        type=str, 
                        nargs="?",
                        default="data/output/" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M'),
                        help='The output path to the mapfile data')    

    parser.add_argument('--debug', 
                        metavar='debug', 
                        type=bool, 
                        nargs='?',
                        default=False,
                        help='To debug')

    parser.add_argument('--minaream2', 
                        metavar='minaream2', 
                        type=int, 
                        nargs='?',
                        default=700,
                        help='area')

    parser.add_argument('--maxaream2', 
                        metavar='maxaream2', 
                        type=int, 
                        nargs='?',
                        default=1200,
                        help='area')

    parser.add_argument('--loadskip', 
                        metavar='level', 
                        type=int, 
                        nargs='?',
                        default=0,
                        help='Disable for running execfile')

    parser.add_argument('--nthreads', 
                        metavar='nthreads', 
                        type=int, 
                        nargs='?',
                        default=128,
                        help='To debug')

    # TODO: Take out of global namespace
    args = parser.parse_args()

    if args.loadskip < 1:
        mapfile = gpd.read_file(args.mapfile)
    mapfile["is_corner"] = 0
    
    window = args.searchwindow
    if args.loadskip < 2:
        filteredmapfile = mapfile.cx[window[0]:window[2], window[1]:window[3]]

    batch_size = len(filteredmapfile)/args.nthreads
    
    pool = Pool(processes=args.nthreads)
    sequence = []
    for i in range(args.nthreads):
        sequence.append((i, filteredmapfile, batch_size, args.adjacentwidth))

    result = pool.map(pcorner, sequence)
    cleaned = [x for x in result if not x is None]
    pool.close()
    pool.join()

    for res in cleaned:
        filteredmapfile["is_corner"].loc[res.index] = res

    filteredmapfile = filter_by_area(filteredmapfile, args.minaream2, args.maxaream2)

    print filteredmapfile[filteredmapfile["is_corner"] == True]
    print sum(filteredmapfile["is_corner"])

    for column in filteredmapfile:
        if filteredmapfile[column].dtype == bool:
            filteredmapfile[column] = filteredmapfile[column].astype(int)

    # Filter by finalize factor
    factor=args.finalizefilterfactor
    if args.debug:
        print("Final window: ", factor*window[0],factor*window[2], factor*window[1],factor*window[3])
    #TODO: Fix this next line:
    #filteredmapfile = filteredmapfile.cx[factor*window[0]:factor*window[2], factor*window[1]:factor*window[3]]

    # Filter by plan
    filteredmapfile = filter_by_plan(filteredmapfile)

    # Filter by regularity
    filteredmapfile = filter_by_regularity(filteredmapfile)

    mkdir_p(args.outputfilepath)
    filteredmapfile.to_file(driver='ESRI Shapefile',filename=args.outputfilepath)


#mapfile[(mapfile["PLAN"].str.contains("131902")) & (mapfile["LOT"] == u'210')].iloc[0].geometry.touches(mapfile[(mapfile["PLAN"].str.contains("131902")) & (mapfile["LOT"] == u'209')].iloc[0].geometry)

#mapfile[(mapfile["PLAN"] == u'SP131902') & (mapfile["LOT"] == u'210')].iloc[0].geometry.touches(mapfile[(mapfile["PLAN"] == u'SP131902') & (mapfile["LOT"] == u'209')].iloc[0].geometry)

# TODO: Test touches algorithm