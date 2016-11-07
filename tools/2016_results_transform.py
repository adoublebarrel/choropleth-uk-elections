#!/usr/bin/python3

import argparse
import csv
import re
from ast import literal_eval
import json

parser = argparse.ArgumentParser(description='Convert an Electoral Comission General Election resulsts csv file into an dictionary indexed by region codes. The resulting JSON structure will be printed to stdout')
parser.add_argument('file', metavar='F', help='the location of the file to be converted' )

args = parser.parse_args()

results = dict()
constituency_properties = (
  'constituency_name',
  'pano',
  'region_id',
  'county',
  'region',
  'rountry',
  'constituency_type'
)

result_properties = (
    'forename',
    'surname',
    'description_on_ballot_paper',
    'votes',
    'share',
    'change',
    'incumbent',
    'party_name_identifier',
    'party_abbreviation'
  )

with open(args.file) as csvfile:
  results_reader = csv.reader(csvfile, dialect='excel')
  headers = next(results_reader);
  headers = tuple(map(lambda h: re.sub(r"_?\W\_?", '', h.lower().strip().replace(' ','_')), headers))

  for row in results_reader:
    row = map(lambda v: (re.match(r"^\d+\.?\d*$", v) and literal_eval(v)) or v, row)
    named_fields = tuple(zip(headers, row))
    full_fields = dict(named_fields)

    if full_fields['constituency_id']:

      constituency_id = full_fields['constituency_id']
      constituency = dict(filter(lambda x: x[0] in constituency_properties, named_fields))
      result = dict(filter(lambda x: x[0] in result_properties, named_fields))

      if constituency_id not in results:
        results[constituency_id] = constituency
        results[constituency_id]['results'] = list()


        results[constituency_id]['results'].append(result)
        results[constituency_id]['results'].sort(key=lambda r: r['votes'], reverse=True)

  print(json.dumps(results))
