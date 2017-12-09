from shapely.geometry import Point
import pyproj
def transform_to_espg(data, epsg=20356):
    return data.to_crs(epsg=epsg)

def transform_to_cart(data, epsg=20356):
    return transform_to_espg(data)

def transform_to_geo(data, epsg=4326):
    return transform_to_espg(data)

def transform_point(pnt, from_epsg, to_epsg):
    return Point(pyproj.transform(pyproj.Proj(init='epsg:' + str(from_epsg)), pyproj.Proj(init='epsg:' + str(to_epsg)), pnt.x, pnt.y))

def transform_point_to_cart(pnt):
    return transform_point(pnt, 4326, 20356)

def transform_point_to_geo(pnt):
    return transform_point(pnt, 20356, 4326)

# Banyo uses 2500, 2500 well.
def box_around_cart_point(cartpnt, x_stretch_m=None, y_stretch_m=None):
    x_stretch_m = x_stretch_m or y_stretch_m
    y_stretch_m = y_stretch_m or x_stretch_m

    return Point(cartpnt.x - x_stretch_m, cartpnt.y + y_stretch_m), Point(cartpnt.x + x_stretch_m, cartpnt.y - y_stretch_m)

