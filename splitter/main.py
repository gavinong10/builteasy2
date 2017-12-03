import geopandas as gpd
import fiona
from shapely.geometry import Point, LineString
import geopy.distance
import pandas as pd
import datetime

import argparse

BRISBANE_POINT=Point(153.025100, -27.469515)

def return_pairs(coords):
    pairs = []
    i = 1
    for i in range(len(coords)):
        pairs.append((coords[i-1], coords[i]))
        i += 1
    return pairs

def get_coords_from_point(point):
    return (point.xy[0][0], point.xy[1][0])

def filter_by_dist(data, point, distance_km=25):
    return data[data.geometry.apply(lambda x: geopy.distance.vincenty(get_coords_from_point(x.centroid), get_coords_from_point(point)).km, convert_dtype=True) <= distance_km]

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
    geom = data.iloc[index]['geometry']

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
            if index + sidelot_candidate_offset + 1 < len(data):
                num_adjacent += side_obj['trunc_line'].intersects(data.iloc[index + sidelot_candidate_offset + 1].geometry)
            if index - (sidelot_candidate_offset + 1) >= 0:
                num_adjacent += side_obj['trunc_line'].intersects(data.iloc[index - (sidelot_candidate_offset + 1)].geometry)
            if num_adjacent >= 2:
                return False

    return True

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
                        help='# kilometers to filter search by')

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

    args = parser.parse_args()
    
    args.debug = True

    mapfile = gpd.read_file(args.mapfile)

    filteredmapfile = filter_by_dist(mapfile, BRISBANE_POINT, args.radialfilter)

    filteredmapfile.reset_index(inplace=True)

    filteredmapfile["is_corner"] = pd.Series(filteredmapfile.index).apply(lambda x: is_corner_lot(filteredmapfile, x, args.offsetrange))

    print filteredmapfile[filteredmapfile["is_corner"] == True]
    print sum(filteredmapfile["is_corner"])

    filteredmapfile.to_file(driver='ESRI Shapefile',filename=args.outputfilepath)

# TODO: Filter by area

#mapfile[(mapfile["PLAN"].str.contains("131902")) & (mapfile["LOT"] == u'210')].iloc[0].geometry.touches(mapfile[(mapfile["PLAN"].str.contains("131902")) & (mapfile["LOT"] == u'209')].iloc[0].geometry)

#mapfile[(mapfile["PLAN"] == u'SP131902') & (mapfile["LOT"] == u'210')].iloc[0].geometry.touches(mapfile[(mapfile["PLAN"] == u'SP131902') & (mapfile["LOT"] == u'209')].iloc[0].geometry)