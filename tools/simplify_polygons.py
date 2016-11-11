#!/usr/bin/env python3

import sys
import argparse
import json

from math import sqrt

parser = argparse.ArgumentParser(description='reduce the accuracy of GeoJson features to reduce file size')
parser.add_argument('geoJSON', metavar='A', help='The geoJSON file to be processed ' )
parser.add_argument('epsilon', metavar='E', help='The distance dimension to use in the algorithm, must be > 0.', type=float )

args = parser.parse_args()

geoJSON = json.load(open(args.geoJSON))
epsilon = args.epsilon

if epsilon <= 0:
    print("Epsilon must be > 0")
    sys.exit()

def PerpindicularDistanceFromLine(linePoint1, linePoint2, point):
    (x1, y1) = linePoint1
    (x2, y2) = linePoint2
    (x0, y0) = point

    y2MinusY1 = y2 - y1
    x2MinusX1 = x2 - x1

    numerator = abs(y2MinusY1 * x0 - x2MinusX1 * y0 + x2 * y1 - y2 * x1)
    denominator = sqrt(y2MinusY1 ** 2 + x2MinusX1 ** 2)

    return numerator / denominator

def FindMaxDistance(polygon):
    maxDistance = 0
    index = 0

    for index, coordinates in enumerate(polygon[1:-2]):
        distance = PerpindicularDistanceFromLine(polygon[0], polygon[-2], coordinates)
        if distance > maxDistance:
            maxDistance = distance
            index = index

    return (maxDistance, index)

def RamerDouglasPeucker(polygon, epsilon):
    # ignore the final point in the polygon (-2 index) as it's the same as the first point.
    # There's no need to close the polygon for displaying via leaflet or mapbox gl
    (maxDistance, index) = FindMaxDistance(polygon)

    while maxDistance > epsilon:

        recResults1 = RamerDouglasPeucker(polygon[0:index], epsilon)
        recResults2 = RamerDouglasPeucker(polygon[index:], epsilon)

        resultList = recResults1 + recResults2
    else :
        resultList = polygon;

    return resultList

for feature in geoJSON['features']:
    if feature['geometry']["type"] == "Polygon":
        for polygon in feature['geometry']['coordinates']:
            polygon = RamerDouglasPeucker(polygon, epsilon)
    else:
        for multipolygon in feature['geometry']['coordinates']:
            for polygon in multipolygon:
                polygon = RamerDouglasPeucker(polygon, epsilon)

print(json.dumps(geoJSON))
