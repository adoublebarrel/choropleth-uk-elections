#!/usr/bin/env python3

import argparse
import json

parser = argparse.ArgumentParser(description='reduce the accuracy of GeoJson features to reduce file size')
parser.add_argument('geoJSON', metavar='A', help='The geoJSON file to be processed ' )
parser.add_argument('accuracy', metavar='numebr of digits', help='The number of decimal places to trim the polygons points to.', type=int )

args = parser.parse_args()

geoJSON = json.load(open(args.geoJSON))
nDigits = args.accuracy

def reduce_polygon_accuracy(polygon, nDigits):
    for coordinates in polygon:
        for point in coordinates:
            point = round(float(point), nDigits)

def reduce_multipolygon_accuracy(multipolygon, nDigits):
    for polygon in multipolygon:
        reduce_polygon_accuracy(polygon, nDigits)

for feature in geoJSON['features']:
    if feature['geometry']["type"] == "Polygon":
        for polygon in feature['geometry']['coordinates']:
            for coordinates in polygon:
                coordinates[0] = round(float(coordinates[0]), nDigits)
                coordinates[1] = round(float(coordinates[1]), nDigits)
    else:
        for multipolygon in feature['geometry']['coordinates']:
            for polygon in multipolygon:
                for coordinates in polygon:
                    coordinates[0] = round(float(coordinates[0]), nDigits)
                    coordinates[1] = round(float(coordinates[1]), nDigits)

print(json.dumps(geoJSON))
