
def get_link(geom, maptype='user', zoom=20):
    centroid_long, centroid_lat = geom.centroid.coords[0]
    zoom_str = "%d" % zoom
    long_str = "%.6f" % centroid_long
    lat_str = "%.6f" % centroid_lat

    if maptype == 'user':
        return "https://www.google.com/maps/@?api=1&map_action=map&center=" + \
        lat_str + "," + long_str + "&&zoom=" + zoom_str + "&basemap=satellite"

    if maptype == 'static':
        key = "AIzaSyDUNUxPMoZfMZrX7iS39C8aB57cnSUYftI"
        return "https://maps.googleapis.com/maps/api/staticmap?center=" + lat_str + "," + long_str + "&zoom=" + zoom_str + "&size=600x600&maptype=satellite&key=" + key
