
from shape.transform import poly_to_lines, get_longest_line, get_longest_untouched_segment, exceeds_angle_variation

class BaseCornerFinder(object):
    def __init__(self):
        super(BaseCornerFinder, self).__init__()

    def configure(self, mf):
        self.mf = mf

    def run(self):
        pass

class DimensionCornerFinder(BaseCornerFinder):
    def __init__(self, adjacentdistance):
        super(DimensionCornerFinder, self).__init__()
        self.adjacentdistance = adjacentdistance

    def run(self):
        # Filter down properties within the immediate area amidst adjacentdistance
        def is_corner_lot(cart_geom, mf, adjacentdistance):
            # For each geometry, get the expanded (x, y) cartesian bounds for it
            x0, y0, x1, y1 = cart_geom.bounds
            # Expand the geometry for each side by 'adjacentdistance' and filter by cartesian
            print "Filtering by cartesian"
            cand_cart, _ = mf.filter_by_cartesian(x0 - adjacentdistance, y0 - adjacentdistance, x1 + adjacentdistance, y1 + adjacentdistance, inplace=False)

            print "Finding all intersecting geoms"
            # Find all candidate geometries that 'intersect'? the target "geom"
            touch_cart_gpd = cand_cart[cand_cart.intersects(cart_geom)]

            print "Getting the longest dimension of bounding rect"
            # Get the longest dimension of a bounding rectangle
            longest_bounding_dim = get_longest_line(poly_to_lines(
                cart_geom.minimum_rotated_rectangle, 2)).length
            
            print "Getting lines from polygon"
            # Create a list of lines that constitute the polygon...
            cart_polygon_lines = poly_to_lines(cart_geom)
            # Iterate through each line of the geom and determine
            # the longest untouched segment
            print "Determining longest untouched segment"
            longest_untouched_segs, longest_untouched_length = get_longest_untouched_segment(
                cart_polygon_lines, touch_cart_gpd.geometry)
            # Filter out those that are smaller than the longest dimension
            if longest_untouched_length > longest_bounding_dim:
                # TODO 2017-12-08 11:06:18 later
                # For the longest segment, filter out those that do not have an angle variation of more than 65 degrees.
                #return exceeds_angle_variation(longest_untouched_segs, 65)
                return True
            
            return False
            
        return self.mf.cart.geometry.apply(
            is_corner_lot, args=(self.mf, self.adjacentdistance))

        

class MinRectCornerFinder(BaseCornerFinder):
    def __init__(self):
        super(MinRectCornerFinder, self).__init__()
    
    def run(self):
        pass
        # Filter down properties within the immediate area amidst adjacentdistance

        # For each geometry, get the minimum rectangle (x, y) cartesian bounds
        # For each of the rectangle sides, at 95% length, see if it intersects with surroundings.
        # If more than 2 sides intersect, it is NOT a side lot

        # Get the longest dimension of a bounding rectangle
        # Iterate through each line of the geom and determine
        # the longest untouched segment
        # Filter out those that are smaller than the longest dimension

        # For the longest segment, filter out those that do not have an angle variation of more than 65 degrees.
