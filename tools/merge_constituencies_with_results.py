#!/usr/bin/python3

import argparse
import json

parser = argparse.ArgumentParser(description='Merge GeoJson features from file B into file A')
parser.add_argument('constituencies', metavar='A', help='The constituencies geoJSON that the results will be added to.' )
parser.add_argument('results', metavar='B', help='The file from which the general election results will be taken from.' )

args = parser.parse_args()

constituencies = json.load(open(args.constituencies))
results = json.load(open(args.results))

for feature in constituencies['features']:
    cid = feature['properties']['id']
    feature['properties']['party'] = results[cid]['results'][0]['party_abbreviation'].lower()

print(json.dumps(constituencies))
