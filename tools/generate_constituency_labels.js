const fs = require('fs');
const polylabel = require('polylabel');
const Transform = require('stream').Transform;

const featuresFileIn = process.argv[2];
const labelsFileOut = process.argv[3];

let constituencies = JSON.parse(fs.readFileSync(featuresFileIn));
let name = "";
for (feature of constituencies.features) {
  name = feature.properties.name.split(' ');
  feature.properties.name = '';

  for (word of name) {
    word = word.toLowerCase();
    if (word == 'and' || word == 'of') {
      feature.properties.name += word;
    } else {
      feature.properties.name += word[0].toUpperCase();
      feature.properties.name += word.substring(1);
    }

    feature.properties.name += ' ';
  }

  feature.properties.name = feature.properties.name.trim();

  if (feature.geometry.type == "MultiPolygon") {
    feature.geometry.type = "Polygon";
    feature.geometry.coordinates = [convertMultiPolygonToPolygon(feature.geometry.coordinates)];
    console.log("convert", feature.geometry.coordinates);
  }

  feature.geometry.coordinates = polylabel(feature.geometry.coordinates, 1.0);
  feature.geometry.type = "Point";
}

fs.writeFileSync(labelsFileOut, JSON.stringify(constituencies,null,1));

/*
 * Quick and dirty conversion of a MultiPolygon to a single Polygon
 * By sampling the largest and smallest X,Y values. The result
 * is a very crued representation, a Polygon of four points but
 * may be good enough for labeling UK and NI parliamentary
 * constituencies.
 */
function convertMultiPolygonToPolygon (multiPolygon) {
  // Initialise the for values to the first set of
  // coordinates of the first Polygon
  largestX = multiPolygon[0][0][0][0];
  smallestX = multiPolygon[0][0][0][0];

  largestY = multiPolygon[0][0][0][1];
  smallestY = multiPolygon[0][0][0][1];

  for (wrapper of multiPolygon) {
    for (polygon of wrapper) {
      for (coordinates of polygon) {
        // Assume coords [x, y]
        if (coordinates[0] > largestX) largestX = coordinates[0];

        if (coordinates[0] < smallestX) smallestX = coordinates[0];

        if (coordinates[1] > largestY) largestY = coordinates[1];

        if (coordinates[1] < smallestY) smallestY = coordinates[1];
      }
    }
  }
  return [
    [largestX, largestY],
    [smallestX, largestY],
    [smallestX, smallestY],
    [largestX, smallestY]
  ];
}
