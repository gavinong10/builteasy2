from shapely.geometry import LineString
import numpy as np

def poly_to_lines(poly_geom, stop=None):
    coords = poly_geom.exterior.coords
    stop = stop or len(coords) - 2
    lines = []
    for i in range(stop):
        lines.append(LineString(coords[i:i+2]))
    if stop is None:
        # Close the polygon
        lines.append(LineString([coords[len(coords) - 1], coords[0]]))
    return lines

def get_longest_line(lines):
    longestlinelength=-1
    longestline=None
    for line in lines:
        if line.length > longestlinelength:
            longestline=line
            longestlinelength = line.length
    return longestline


def extract_untouched_segment_in_dir(geoms, segment_lines, lines, offset, popidx=0):
    if len(lines) == 0:
        return
    item = lines.pop(popidx)
    while geoms.intersects(item).sum() == offset:
        segment_lines.append(item)
        try:
            item = lines.pop(popidx)
        except:
            # No more lines to pop
            return

# modifies lines
def pull_untouched_segment_lines(lines, geoms, offset=0):
    segment_lines = []

    extract_untouched_segment_in_dir(
        geoms, segment_lines, lines, offset, popidx=0)

    extract_untouched_segment_in_dir(
        geoms, segment_lines, lines, offset, popidx=-1)

    return segment_lines

def get_longest_untouched_segment(cart_lines, cart_geoms, contains_self=True):
    # If cart_geoms contains self, offset is 1
    offset = 1 if contains_self else 0
    # Make a copy of cart_lines
    cart_lines = cart_lines[:]
    longest_seg_length = -1
    longest_segment_lines = []
    # Start with a line segment and pop in BOTH directions
    # Pop forwards
    while len(cart_lines) > 0:
        segment_lines = pull_untouched_segment_lines(
            cart_lines, cart_geoms, offset)

        seg_length = sum([line.length for line in segment_lines])
        if seg_length > longest_seg_length:
            longest_seg_length = seg_length
            longest_segment_lines = segment_lines
            
    return longest_segment_lines, longest_seg_length


def angle_between_straight_lines(p1, p2, degrees=True):
    # TODO: 2017-12-08 11:06:01 Later - Test me 
    p1_coords = p1.coords
    p2_coords = p2.coords
    if len(p1_coords) != 2 or len(p2_coords) != 2:
        raise Exception("Coordinates not of length = 2! Not a straight line.")
    
    p1_start, p1_end = p1_coords
    p2_start, p2_end = p2_coords

    v1 = p1_end[0] - p1_start[0] + (p1_start[1] - p1_end[1]) * 1j
    v2 = p2_end[0] - p2_start[0] + (p2_start[1] - p2_end[1]) * 1j
    
    ang1, ang2 = np.angle(v1, v2, deg=True)
    return ang2 - ang1


def cumulative_angle(lines, degrees=True):
    # TODO 2017-12-08 11:06:51 later
    pass

def exceeds_angle_variation(line_segs, angle_degrees):
    return cumulative_angle(line_segs) >= angle_degrees
