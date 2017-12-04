import geopandas as gpd
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mapfile', 
                        metavar='file path', 
                        type=str, 
                        nargs='?',
                        default="data/boundaries_gdb/data.gdb",
                        help='The path to the mapfile data')

    parser.add_argument('--outputfilepath', 
                        metavar=('file path',), 
                        type=str, 
                        nargs=1,
                        help='The output path to the mapfile data')

    parser.add_argument('--start', 
                        metavar='indexstart', 
                        type=int, 
                        nargs='?',
                        default=0,
                        help='start index position')

    parser.add_argument('--end', 
                        metavar='indexend', 
                        type=int, 
                        nargs='?',
                        default=1000,
                        help='end index position')

    args = parser.parse_args()

    mapfile = gpd.read_file(args.mapfile)
    mapfile = mapfile.iloc[args.start:args.end]
    mapfile.to_file(driver='ESRI Shapefile',filename=args.outputfilepath[0])