#!/usr/bin/env python3

import sys
import argparse
import json

from math import sqrt
from decimal import *

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
  (x1, y1) = (linePoint1[0], linePoint1[1])
  (x2, y2) = (linePoint2[0], linePoint2[1])
  (x0, y0) = (point[0], point[1])

  y2MinusY1 = y2 - y1
  x2MinusX1 = x2 - x1

  numerator = abs(y2MinusY1 * x0 - x2MinusX1 * y0 + x2 * y1 - y2 * x1)
  denominator = sqrt(y2MinusY1 ** 2 + x2MinusX1 ** 2)

  return numerator / denominator

def FindMaxDistance(polygon, printResult = False):
  maxDistance = 0.0
  maxDistanceIndex = False
  #print(polygon[0])
  #print(polygon[-1])
  #print(coordinates)

  if printResult:
    print(polygon)

  for index, coordinates in enumerate(polygon[1:-1]):
    distance = PerpindicularDistanceFromLine(polygon[0], polygon[-1], coordinates)

    if printResult:
      print(distance)

    if distance > maxDistance:
      maxDistance = distance
      maxDistanceIndex = index + 1

  return (maxDistanceIndex, maxDistance)

def RamerDouglasPeucker(polygon, epsilon):
  keepPoints = [0]
  pointIndices = []
  pointIndex = False

  # See if there is at least one point worth keeping
  (maxDistanceIndex, maxDistance) = FindMaxDistance(polygon)
  #if (maxDistance < epsilon):
  #print(maxDistance)


  if maxDistance > epsilon:
    keepPoints.append( maxDistanceIndex)
    pointIndex = 1

  keepPoints.append(len(polygon) -1)
  keepPoints.append(0)

  while pointIndex:
    #pdb.set_trace()
    previousPointIndex = keepPoints[pointIndex - 1]
    currentPointIndex = keepPoints[pointIndex]
    nextPointIndex = keepPoints[pointIndex + 1] + 1

    # Check points before pointIndex
    (maxDistanceIndex, maxDistance) = FindMaxDistance(polygon[previousPointIndex:currentPointIndex + 1])

    #print(maxDistance)
    if maxDistance > epsilon:
      keepPoints.insert(pointIndex, maxDistanceIndex + previousPointIndex)
      pointIndices.append(pointIndex)
      pointIndex += 1

    # Check points after point index
    (maxDistanceIndex, maxDistance) = FindMaxDistance(polygon[currentPointIndex:nextPointIndex])

    if maxDistance > epsilon:
      keepPoints.insert(pointIndex + 1, maxDistanceIndex + currentPointIndex)
      pointIndices.append(pointIndex + 1)

    if len(pointIndices):
      pointIndex = pointIndices.pop(len(pointIndices) - 1)
    else:
      pointIndex = False

  # for index, value in enumerate(polygon):
  #   if index not in keepPoints:
  #     prevIndex = index - 1
  #     nextIndex = index + 1

  #     while prevIndex not in keepPoints:
  #       prevIndex -= 1

  #     while nextIndex not in keepPoints:
  #       nextIndex += 1

  #     nextIndex += 1

  #     (i, v) = FindMaxDistance(polygon[prevIndex:nextIndex], True)

  #     print(v > epsilon)

  #print('keeping {0} of {1} points'.format(len(keepPoints), len(polygon)))
  return [polygon[i] for i in keepPoints]

for feature in geoJSON['features']:
    if feature['geometry']["type"] == "Polygon":
      #print(feature['properties']['name'])
      for polygon in feature['geometry']['coordinates']:
        simplerPolygon = RamerDouglasPeucker(polygon[0:-1], epsilon)

        polygonLength = len(polygon)
        e = epsilon
        while (len(simplerPolygon) < polygonLength) and len(simplerPolygon) < 10:
          e = e / 2.5
          simplerPolygon = RamerDouglasPeucker(polygon[0:-1], e)

        polygon[:] = simplerPolygon
        if polygon[0] != polygon[-1]:
          print('Uh oh {0}!'.format(feature['properties']['name']))

    else:
      p = []
      for multipolygon in feature['geometry']['coordinates']:
        for polygon in multipolygon:
          simplerPolygon = RamerDouglasPeucker(polygon[0:-1], epsilon)

          polygonLength = len(polygon)
          e = epsilon
          while (len(simplerPolygon) < polygonLength) and len(simplerPolygon) < 10:
            e = e / 2.5
            simplerPolygon = RamerDouglasPeucker(polygon[0:-1], e)

          polygon[:] = simplerPolygon

          if polygon[0] != polygon[-1]:
            print('Uh oh {0}!'.format(feature['properties']['name']))

print(json.dumps(geoJSON))
