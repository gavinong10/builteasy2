import geopandas as gpd
import fiona
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

def DistFilterThreading(i, data, batch_size, distance_km, point):
    batch_data = data[i * batch_size: (i+1) * batch_size]
    return batch_data[batch_data.geometry.apply(lambda x: geopy.distance.vincenty(get_coords_from_point(x.centroid), get_coords_from_point(point)).km, convert_dtype=True) <= distance_km]

def pdist(i):
    return DistFilterThreading(*i)

def filter_by_dist(data, point, n_threads, distance_km=25):
    batch_size = len(data)/n_threads
    #threads = []
    thread_fns = []
    sequence = [(i, data, batch_size, distance_km, point) for i in range(n_threads)]
    result = pool.map(pdist, sequence)
    cleaned = [x for x in result if not x is None]
    pool.close()
    pool.join()
    
    return pd.concat(cleaned)

def filter_by_area(data, min_area_m2=700, max_area_m2=1200):
    area = data.geometry.area * 1e10
    return data[(area >= min_area_m2) & (area <= max_area_m2)]

def get_by_lot(data, plan, lot):
    # Might return more than one entry
    plan = unicode(plan)
    lot = unicode(lot)
    entry = data[(data["PLAN"] == plan) & (data["LOT"] == lot)]
    return entry

def is_corner_lot(data, index, offset_range=16):
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

    # Get the minimum rotated rectangle bounding box
    min_rect_bbox = geom.minimum_rotated_rectangle
    # Extract the centroids and lengths of each side
    corner_coords = zip(*geom.minimum_rotated_rectangle.exterior.xy)
    side_objs = [{"pair": pair, "orig_line": LineString(pair)} for pair in return_pairs(corner_coords)]
    for side_obj in side_objs:
        side_obj["length_m"] = geopy.distance.vincenty(side_obj["pair"][0], side_obj["pair"][1]).m
        side_obj["centroid"] = side_obj["orig_line"].centroid
        # Generate a set of lengths that is 50% in length
        side_obj["trunc_line"] = LineString((Point(((pair[0][0] + side_obj["centroid"].xy[0][0]) * 0.5, (pair[0][1] + side_obj["centroid"].xy[1][0]) * 0.5)), Point(((pair[1][0]  + side_obj["centroid"].xy[0][0]) * 0.5, (pair[1][1] + side_obj["centroid"].xy[1][0]) * 0.5))))

    # If >= 2 sides do NOT intersect, then it is a corner lot    
    num_adjacent = 0
    for sidelot_candidate_offset in range(offset_range/2):
        for side_obj in side_objs:
            if index + sidelot_candidate_offset + 1 in data.index:
                num_adjacent += side_obj['trunc_line'].intersects(data.loc[index + sidelot_candidate_offset + 1].geometry)
            if index - (sidelot_candidate_offset + 1) in data.index:
                num_adjacent += side_obj['trunc_line'].intersects(data.loc[index - (sidelot_candidate_offset + 1)].geometry)
            if num_adjacent >= 2:
                return False

    return True

# class CornerLotIdentifierThread (threading.Thread):
#    def __init__(self, threadID, name, i, filteredmapfile, offsetrange, indices, batch_size):
#       threading.Thread.__init__(self)
#       self.threadID = threadID
#       self.name = name
#       self.i = i
#       self.filteredmapfile = filteredmapfile
#       self.offsetrange = offsetrange
#       self.thread_indices = indices[i * batch_size: (i+1) * batch_size]
#       self.batch_res = None

      
#    def run(self):
#       self.batch_res = self.thread_indices.to_series().apply(lambda x: is_corner_lot(self.filteredmapfile, x, self.offsetrange))
#       return self.batch_res

def CornerLotIdentifyThreading(i, filteredmapfile, offsetrange, indices, batch_size):
    thread_indices = indices[i * batch_size: (i+1) * batch_size]
    return thread_indices.to_series().apply(lambda x: is_corner_lot(filteredmapfile, x, offsetrange))

def pcorner(i):
    return CornerLotIdentifyThreading(*i)

def main():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process arguments to the data analyzer.')
    parser.add_argument('--mapfile', 
                        metavar='file path', 
                        type=str, 
                        nargs='?',
                        default="data/boundaries_gdb/data.gdb",
                        help='The path to the mapfile data')

    parser.add_argument('--radialfilter', 
                        metavar='radius', 
                        type=int, 
                        nargs='?',
                        default=30,
                        help='# kilometers to filter search by')

    parser.add_argument('--offsetrange', 
                        metavar='range', 
                        type=int, 
                        nargs='?',
                        default=1000,
                        help='# surrounding(ish) listings to examine')

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
    parser.add_argument('--center', 
                        metavar=('longitude', 'latitude'), 
                        type=float, 
                        nargs=2,
                        default=BRISBANE_COORDS,
                        help='Center point of search (Default is Brisbane City')

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

    parser.add_argument('--nthreads', 
                        metavar='nthreads', 
                        type=int, 
                        nargs='?',
                        default=128,
                        help='To debug')

    # TODO: Take out of global namespace
    args = parser.parse_args()
    
    center = Point(*args.center)
    args.debug = True

    mapfile = gpd.read_file(args.mapfile)

    pool = Pool(processes=args.nthreads)
    filteredmapfile = filter_by_dist(mapfile, center, args.nthreads, args.radialfilter)
    filteredmapfile["is_corner"] = 0

    #filteredmapfile.reset_index(inplace=True)

    batch_size = len(filteredmapfile)/args.nthreads
    
    indices = filteredmapfile.index

    pool = Pool(processes=args.nthreads)
    sequence = [(i, filteredmapfile, args.offsetrange, indices, batch_size) for i in range(args.nthreads)]
    result = pool.map(pcorner, sequence)
    cleaned = [x for x in result if not x is None]
    pool.close()
    pool.join()

    for res in cleaned:
        print filteredmapfile.index
        filteredmapfile["is_corner"].loc[res.index] = res.astype(int)

    filteredmapfile = filter_by_area(filteredmapfile, args.minaream2, args.maxaream2)

    print filteredmapfile[filteredmapfile["is_corner"] == True]
    print sum(filteredmapfile["is_corner"])

    mkdir_p(args.outputfilepath)
    filteredmapfile.to_file(driver='ESRI Shapefile',filename=args.outputfilepath)

# TODO: Filter by area

#mapfile[(mapfile["PLAN"].str.contains("131902")) & (mapfile["LOT"] == u'210')].iloc[0].geometry.touches(mapfile[(mapfile["PLAN"].str.contains("131902")) & (mapfile["LOT"] == u'209')].iloc[0].geometry)

#mapfile[(mapfile["PLAN"] == u'SP131902') & (mapfile["LOT"] == u'210')].iloc[0].geometry.touches(mapfile[(mapfile["PLAN"] == u'SP131902') & (mapfile["LOT"] == u'209')].iloc[0].geometry)