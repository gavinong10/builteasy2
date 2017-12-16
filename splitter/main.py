#sys.argv = ['', '--mapfile', 'data/boundaries_shp/Property_boundaries___DCDB_Lite.shp', '--debug', 'True']
#sys.argv = ['', '--mapfile', 'data/boundaries_shp/Property_boundaries___DCDB_Lite.shp', '--debug', 'True', '--alt', '1']
#import sys; sys.argv = ['', '--mapfile', 'data/boundaries_shp/Property_boundaries___DCDB_Lite.shp', '--debug', 'True', '--suburb', 'BANYO']; execfile('main.py')
#import sys; sys.argv = ['', '--mapfile', 'data/truncated/banyo/shp/geo/out.shp', '--debug', 'True', '--suburb', 'BANYO']; execfile('main.py')
#import sys; sys.argv = ['', '--mapfile', 'data/bcc/shp/geo/out.shp', '--debug', 'True', '--nthreads', '36', '--suburb', 'BANYO']; execfile('main.py')
#import sys; sys.argv = ['', '--mapfile', 'data/bcc/shp/geo/out.shp', '--debug', 'True', '--nthreads', '36', '--suburb', 'BROOKFIELD:']; execfile('main.py')

#import sys; sys.argv = ['', '--mapfile', 'data/boundaries_shp/Property_boundaries___DCDB_Lite.shp', '--debug', 'True', '--suburb', 'BRISBANE CITY', '--perimeterdist', '30000', '--alt', '1', '--alt_truncated_output', 'data/bcc/shp']; execfile('main.py')

#sys.argv = ['', '--mapfile', 'data/truncated/banyo/shp/Property_boundaries___DCDB_Lite.shp', '--debug', 'True', '--alt', '1']

import geopandas as gpd
from shapely.geometry import Point, LineString
import geopy.distance
import pandas as pd
import datetime
import threading
import logging

import argparse
from multiprocessing import Pool
from filterfetch.filterfetch import transform_point_to_cart, box_around_cart_point
from filterfetch.data import Mapfile

from algorithms.cornerfinder.cornerfinder import DimensionCornerFinder

import errno    
import os

# Shapely logging fix
logging.basicConfig()

BRISBANE_COORDS=(153.025100, -27.469515)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

#################
def filter_search_scope(mf, centerpoint, perimeterdist):
        center_cart_point = transform_point_to_cart(Point(*centerpoint))
        startpnt, endpnt = box_around_cart_point(center_cart_point, perimeterdist/2)
        mf.filter_by_cartesian(startpnt.x, startpnt.y, endpnt.x, endpnt.y)

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

    parser.add_argument('--adjacentdist', 
                        metavar='meters', 
                        type=float, 
                        nargs='?',
                        default=5,
                        help='The distance to search around a property')

    # TODO 2017-12-08 11:08:31
    # parser.add_argument('--finalizefilterfactor', 
    #                     metavar='factor', 
    #                     type=float, 
    #                     nargs='?',
    #                     default=0.9,
    #                     help='The factor to reduce the result by to cut off the edge')

    parser.add_argument('--suburb', 
                        metavar="suburb name e.g. BANYO", 
                        type=str, 
                        nargs='?',
                        default="", #banyo
                        help='The suburb window centerpoint to search for properties')

    parser.add_argument('--perimeterdist', 
                        metavar='meters', 
                        type=float, 
                        nargs='?',
                        default=7000,
                        help='The distance to search around the centerpoint')

    parser.add_argument('--outputfilepath', 
                        metavar=('file path',), 
                        type=str, 
                        nargs="?",
                        default="data/output/",
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
                        default=600,
                        help='area')

    parser.add_argument('--maxaream2', 
                        metavar='maxaream2', 
                        type=int, 
                        nargs='?',
                        default=1200,
                        help='area')

    parser.add_argument('--loadskip', 
                        metavar='level', 
                        type=str, 
                        nargs='?',
                        default="",
                        help='Disable for running execfile')

    parser.add_argument('--alt',
                        metavar='int',
                        type=int,
                        nargs='?',
                        default=0,
                        help='To debug')

    parser.add_argument('--alt_truncated_output',
                        metavar='path',
                        type=str,
                        nargs='?',
                        default="data/truncated/banyo/shp",
                        help='To debug')

    parser.add_argument('--multithread',
                        metavar='bool',
                        type=bool,
                        nargs='?',
                        default=True,
                        help='To multithread')

    parser.add_argument('--nthreads', 
                        metavar='nthreads', 
                        type=int, 
                        nargs='?',
                        default=4,
                        help='How many threads if multithreading')

    parser.add_argument('--suburbcoordsfile',
                        metavar='path',
                        type=str,
                        nargs='?',
                        default="../geocoding/data/suburb_coordinates_bcc.csv",
                        help='Where to get suburb geocoordinates')

    # TODO: 2017-12-08 11:06:32 later: Take out of global namespace
    args = parser.parse_args()
    debug = args.debug

    if debug:
        print "Parsed arguments: ", args
    if args.loadskip != "read":
        if debug:
            print "Reading mapfile..."
        mapfile = gpd.read_file(args.mapfile)

    suburbcoords = pd.read_csv(args.suburbcoordsfile)
    suburbs_to_process = []

    if args.suburb == "":
        suburbs_to_process = suburbcoords
    elif args.suburb[-1] == ":":
         # Process everything after this marker, inclusive
        idx = suburbcoords[suburbcoords["Suburb"]
                           == args.suburb[:-1]].index
        suburbs_to_process = suburbcoords.loc[idx:]
    else:
        suburbs_to_process = suburbcoords[suburbcoords["Suburb"]
                                          == args.suburb]

    for _, row in suburbs_to_process.iterrows():
        centerpoint = float(row["Longitude"]), float(row["Latitude"])

        mf = Mapfile(mapfile)

        # TODO: 2017-12-08 11:06:41 Verify that mf is successfully filtered
        if debug:
            print "Filtering down search scope around center point: ", centerpoint
            print "Perimeter distance = ", args.perimeterdist
        filter_search_scope(mf, centerpoint, args.perimeterdist)

        if args.alt == 1:
            print "Alternate operation mode 1..."
            filepath = args.alt_truncated_output + "/geo/"
            mkdir_p(filepath)
            filename = filepath + "out.shp"
            mf.geo.to_file(driver='ESRI Shapefile',
                        filename=filename)
            print "Saved to " + filename
            exit(0)

        # Sets mf.is_corner_series
        if debug:
            print "Marking corners..."
        mf.mark_corners(DimensionCornerFinder(args.adjacentdist), args.multithread, args.nthreads)

        mf.geo["is_corner"] = mf.is_corner_series.astype(int)

        # Filter by plan
        if debug:
            print "Filtering by plan..."
        mf.filter_by_plan()

        # Filter by regularity
        if debug:
            print "Filtering by regularity..."
        mf.filter_by_regularity()

        # Filter by area
        if debug:
            print "Filtering by area..."
        mf.filter_by_area(args.minaream2, args.maxaream2)

        # Filter out the ends
        if debug:
            print "Filtering out the edges (TODO)..."

        # Only use corners
        formatting_gpd = mf.geo[mf.is_corner_series == 1]
        folderpath = args.outputfilepath + row["Suburb"] + "/"
        mkdir_p(folderpath)
        finaloutputpath = folderpath + \
            datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".shp"

        if len(formatting_gpd) > 0:
            formatting_gpd.to_file(driver='ESRI Shapefile',
                               filename=finaloutputpath)
    # Generate webpage
    
    
#     mkdir_p(args.outputfilepath) TODO later
#     filteredmapfile.to_file(driver='ESRI Shapefile',filename=args.outputfilepath)
