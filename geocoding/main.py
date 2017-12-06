from geopy.geocoders import ArcGIS, Baidu, Bing, DataBC, GeoNames, GeocodeFarm, GeocoderDotUS, GeocoderNotFound, GoogleV3, IGNFrance, LiveAddress, NaviData, Nominatim, OpenCage, OpenMapQuest, Photon, What3Words, YahooPlaceFinder, Yandex
import pandas as pd
import time

def try_and_recover(fn, sleep=3, retry=3, exceptions=(Exception,), debug=False, arguments=[]):
    for _ in range(retry):
        try:
            if debug:
                print "Arguments: ", arguments
            return fn(*arguments)
        except exceptions as e:
            time.sleep(3)
    return None

#geocoders = [ArcGIS(), Baidu(), Bing(), DataBC(), GeoNames(), GeocodeFarm(), GeocoderDotUS(), GoogleV3(), IGNFrance(), LiveAddress(), NaviData(), Nominatim(), OpenCage(), OpenMapQuest(), Photon(), What3Words(), YahooPlaceFinder(), Yandex()]
geocoders = [ArcGIS]

data = pd.read_csv('data/20170914000odstreet.csv')
data["LAT"] = None
data["LONG"] = None

suburbs = sorted(list(data["SUBURB"].unique()))

for suburb in suburbs:
    geolocator = ArcGIS()
    location = try_and_recover(geolocator.geocode, arguments=(suburb + ", QUEENSLAND, AUSTRALIA",))
    if location is not None:
        print suburb, ": ", location.latitude, location.longitude
        data[data["SUBURB"] == suburb]["LAT"] = location.latitude
        data[data["SUBURB"] == suburb]["LONG"] = location.longitude
    else:
        print suburb, " failed!"

data.to_csv('data/20170914000odstreetwithcoords.csv')

# for geolocator in geocoders:
#     print geolocator
#     geolocator = geolocator()
#     location = geolocator.geocode("175 5th Avenue NYC")
#     print(location.address)


