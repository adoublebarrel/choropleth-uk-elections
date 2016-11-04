#!/usr/bin/python3

import argparse
import json

parser = argparse.ArgumentParser(description='Merge GeoJson features from file B into file A')
parser.add_argument('fileA', metavar='A', help='The file that features will be added to.' )
parser.add_argument('fileB', metavar='B', help='The file that features will be taken from.' )

args = parser.parse_args()

fileA = json.load(open(args.fileA))
fileB = json.load(open(args.fileB))

for feature in fileA['features']:
    feature['properties']['name'] = feature['properties']['PCON13NM']
    feature['properties']['id'] = feature['properties']['PCON13CD']
    feature['properties']['cdo'] = feature['properties']['PCON13CDO']

    del feature['properties']['PCON13NM']
    del feature['properties']['PCON13CD']
    del feature['properties']['PCON13CDO']

for feature in fileB['features']:
    feature['properties']['name'] = feature['properties']['PC_NAME']
    feature['properties']['id'] = feature['properties']['PC_ID']
    feature['properties']['cdo'] = feature['properties']['OBJECTID']

    del feature['properties']['PC_NAME']
    del feature['properties']['PC_ID']
    del feature['properties']['OBJECTID']

    fileA['features'].append(feature)


print(json.dumps(fileA))
