#!/usr/bin/env python3

import sys
import argparse
import json

from math import sqrt

import pdb

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
    maxDistance = 0.0
    maxDistanceIndex = False

    for index, coordinates in enumerate(polygon[1:-2]):
        distance = PerpindicularDistanceFromLine(polygon[0], polygon[-1], coordinates)
        #print(polygon[0])
        #print(polygon[-1])
        #print(coordinates)
        #print(distance)
        if distance > maxDistance:
            maxDistance = distance
            maxDistanceIndex = index + 1

    return (maxDistanceIndex, maxDistance)

def RamerDouglasPeucker(polygon, epsilon):
    keepPoints = [0, (len(polygon) - 1)]
    pointIndices = []
    pointIndex = False

    # See if there is at least one point worth keeping
    (maxDistanceIndex, maxDistance) = FindMaxDistance(polygon)
    if maxDistance > epsilon:
        keepPoints.insert(1, maxDistanceIndex)
        pointIndex = 1

    while pointIndex:
        #pdb.set_trace()
        previousPointIndex = keepPoints[pointIndex - 1]
        currentPointIndex = keepPoints[pointIndex]
        nextPointIndex = keepPoints[pointIndex + 1]

        (maxDistanceIndex, maxDistance) = FindMaxDistance(polygon[previousPointIndex:currentPointIndex])

        if maxDistance > epsilon:
            keepPoints.insert(pointIndex, maxDistanceIndex + previousPointIndex)
            pointIndices.append(pointIndex)
            pointIndex += 1

        (maxDistanceIndex, maxDistance) = FindMaxDistance(polygon[currentPointIndex:nextPointIndex])

        if maxDistance > epsilon:
            keepPoints.insert(pointIndex + 1, maxDistanceIndex + currentPointIndex)
            pointIndices.append(pointIndex + 1)

        if len(pointIndices):
            pointIndex = pointIndices.pop(len(pointIndices) - 1)
        else:
            pointIndex = False

    return [polygon[i] for i in keepPoints]

for feature in geoJSON['features']:
    if feature['geometry']["type"] == "Polygon":
        for polygon in feature['geometry']['coordinates']:
            polygon[:] = RamerDouglasPeucker(polygon[0:-2], epsilon)

    else:
        for multipolygon in feature['geometry']['coordinates']:
            for polygon in multipolygon:
                polygon[:] = RamerDouglasPeucker(polygon[0:-2], epsilon)

print(json.dumps(geoJSON))
