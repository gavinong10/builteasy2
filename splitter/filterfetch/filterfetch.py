

from shapely.geometry import Point

# def get_by_lot(data, plan, lot):
#     # Might return more than one entry
#     # plan = unicode(plan)
#     lot = unicode(lot)
#     entry = data[(data["PLAN"] == plan) & (data["LOT"] == lot)]
#     return entry

# def get_points(geom):
#     pass

# def filter_by_surrounding(data, targetgeom, coordoffset):
#     pass

# def filter_by_plan(data):
#     return data[data["PLAN"].str.startswith("SP") | data["PLAN"].str.startswith("RP")]

# def filter_by_regularity(data, factor=0.8):
#     regularity = data.geometry.apply(lambda x: x.area / x.minimum_rotated_rectangle.area)
#     return data[regularity > factor]

# def filter_by_area(data, min_area_m2=700, max_area_m2=1200):
#     area = data.geometry.area * 1e10
#     return data[(area >= min_area_m2) & (area <= max_area_m2)]

# def filter_by_coords(long1, lat1, long2, lat2):
#     return mapfile.cx[long1:long2, lat1:lat2]   

def transform_to_espg(data, epsg=20356):
    return data.to_crs(epsg=epsg)

def transform_to_cart(data, epsg=20356):
    return transform_to_espg(data)

def transform_to_geo(data, epsg=4326):
    return transform_to_espg(data)

def transform_point(pnt, from_epsg, to_epsg):
    return pyproj.transform(pyproj.Proj(init='epsg:' + str(from_epsg)), pyproj.Proj(init='epsg:' + str(to_epsg)), pnt.x, pnt.y)

def transform_point_to_cart(pnt):
    return transform_point(pnt, 4326, 20356)

def transform_point_to_geo(pnt):
    return transform_point(pnt, 20356, 4326)

# Banyo uses 2500, 2500 well.
def box_around_cart_point(cartpnt, x_stretch_m=None, y_stretch_m=None):
    x_stretch_m = x_stretch_m or y_stretch_m
    y_stretch_m = y_stretch_m or x_stretch_m

    return Point(cartpnt.x - x_stretch_m, cartpnt.y + y_stretch_m), Point(cartpnt.x + x_stretch_m, cartpnt.y - y_stretch_m)

