
import math

def point_distance(p1, p2):
    xp = math.pow(p2[0] - p1[0], 2)
    yp = math.pow(p2[1] - p1[1], 2)
    return math.sqrt(xp + yp)

def point_direction(point):
    if point[0] == 0:
        if point[1] > 0: dir = 1.5708
        else: dir = -1.5708
    else: dir = math.atan(point[1]/point[0])
    if point[0] < 0:
        dir += 3.1415
    elif point[1] < 0:
        dir += 6.2832
    return dir