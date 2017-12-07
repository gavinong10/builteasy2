class Mapfile(object):
    def __init__(self, geo, cart=None):
        self.geo = geo
        self.cart = cart
        if cart is None:
            self.cart = self._transform_to_espg()
        

    def get_by_lot(self, plan, lot, geo=True, to_mf=False):
        # Might return more than one entry
        # plan = unicode(plan)
        data = self.geo if geo else self.cart
        lot = unicode(lot)
        entry = data[(data["PLAN"] == plan) & (data["LOT"] == lot)]
        if to_mf:
            return Mapfile(entry, self.cart.loc[entry.index]) if geo else Mapfile(self.geo.loc[entry.index], entry)
        return entry

    def get_points(geom, geo=True, to_mf=False):
        pass

    def filter_by_surrounding(self, targetgeom, coordoffset, geo=True, to_mf=False):
        pass

    def filter_by_plan(self, geo=True, to_mf=False):
        data = self.geo if geo else self.cart
        return data[data["PLAN"].str.startswith("SP") | data["PLAN"].str.startswith("RP")]

    def filter_by_regularity(self, factor=0.8, geo=True, to_mf=False):
        data = self.geo if geo else self.cart
        regularity = data.geometry.apply(lambda x: x.area / x.minimum_rotated_rectangle.area)
        return data[regularity > factor]

    def filter_by_area(self, min_area_m2=700, max_area_m2=1200, geo=True, to_mf=False):
        data = self.geo if geo else self.cart
        area = data.geometry.area * 1e10
        return data[(area >= min_area_m2) & (area <= max_area_m2)]

    def filter_by_coords(long1, lat1, long2, lat2, geo=True, to_mf=False):
        data = self.geo if geo else self.cart
        return data.cx[long1:long2, lat1:lat2]   

    def filter_by_cartesian(x1, y1, x2, y2, geo=False, to_mf=False):
        data = self.geo if geo else self.cart
        return data.cx[long1:long2, lat1:lat2]   

    def _transform_to_espg(self, epsg=20356, geo=True, to_mf=False):
        data = self.geo if geo else self.cart
        return data.to_crs(epsg=epsg)