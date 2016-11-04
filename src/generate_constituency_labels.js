const fs = require('fs');
const polylabel = require('polylabel');
const Transform = require('stream').Transform;

const featuresFileIn = process.argv[2];
const labelsFileOut = process.argv[3];

let constituencies = JSON.parse(fs.readFileSync(featuresFileIn));

for (feature of constituencies.features) {
  console.log(feature);
  feature.geometry.coordinates = polylabel(feature.geometry.coordinates, 1.0);
  feature.geometry.type = "Point";
}

fs.writeFileSync(labelsFileOut, JSON.stringify(constituencies,null,1));
