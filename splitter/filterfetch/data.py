class Mapfile(object):
    def __init__(self, geo, cart=None):
        self.geo = geo
        self.cart = cart
        if cart is None:
            self.cart = self.__transform_to_espg()
        self.is_corner_series = None

    def get_by_lot(self, plan, lot, geo=True, to_mf=False):
        # Might return more than one entry
        # plan = unicode(plan)
        data = self.geo if geo else self.cart
        lot = unicode(lot)
        entry = data[(data["PLAN"] == plan) & (data["LOT"] == lot)]
        if to_mf:
            return Mapfile(entry, self.cart.loc[entry.index]) if geo else Mapfile(self.geo.loc[entry.index], entry)
        return entry

    def filter_by_plan(self, inplace=True):
        geo = self.geo[self.geo["PLAN"].str.startswith(
            "SP") | self.geo["PLAN"].str.startswith("RP")]
        cart = self.cart.loc[geo.index]
        if inplace:
            self.geo = geo
            self.cart = cart
        else:
            return geo, cart

    def filter_by_regularity(self, factor=0.8, inplace=True):
        regularity = self.cart.geometry.apply(lambda x: x.area / x.minimum_rotated_rectangle.area)
        geo = self.geo[regularity > factor]
        cart = self.cart.loc[geo.index]
        if inplace:
            self.geo = geo
            self.cart = cart
        else:
            return geo, cart

    def filter_by_area(self, min_area_m2=700, max_area_m2=1200, inplace=True):
        area = self.cart.geometry.area
        cart = self.cart[(area >= min_area_m2) & (area <= max_area_m2)]
        geo = self.geo.loc[cart.index]
        if inplace:
            self.cart = cart
            self.geo = geo
        else:
            return geo, cart

    def filter_by_coords(self, long1, lat1, long2, lat2, inplace=True):
        geo = self.geo.cx[long1:long2, lat1:lat2]
        cart = self.cart.loc[geo.index]
        if inplace:
            self.geo = geo
            self.cart = cart
        else:
            return geo, cart

    #inplace=False not yet implemented
    def filter_by_cartesian(self, x1, y1, x2, y2, inplace=True):
        cart = self.cart.cx[x1:x2, y1:y2]
        geo = self.geo.loc[cart.index]
        if inplace:
            self.cart = cart
            self.geo = geo
        else:
            return cart, geo

    def __transform_to_espg(self, epsg=20356, geo=True):
        data = self.geo if geo else self.cart
        return data.to_crs(epsg=epsg)

    def mark_corners(self, cornerfinder, multithread=False, n_workers=4):
        cornerfinder.configure(self)
        if multithread:
            self.is_corner_series = cornerfinder.run_multithread(n_workers)
        else:
            self.is_corner_series = cornerfinder.run()
        return self.is_corner_series
