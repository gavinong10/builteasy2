
def get_link(geom, zoom=17.9):
    centroid_long, centroid_lat = geom.centroid.coords[0]
    zoom_str = "%.1f" % zoom
    long_str = "%.6f" % centroid_long
    lat_str = "%.6f" % centroid_lat

    return "http://maps.eatlas.org.au/index.html?intro=false&z=" + zoom_str + "&ll=" + long_str + "," + lat_str + "&l0=ea_ea%3AQLD_DNRM_Property-boundaries-DCDB_Aug-2016,ea_World_NE2-coast-cities-reefs_Baselayer,google_HYBRID,google_TERRAIN,google_SATELLITE,google_ROADMAP,ea_ea%3AQLD_DNRM_Property-boundaries-DCDB-July-2012&v0=,f,f,f,,f,f&intro=false"
