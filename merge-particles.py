#!python

import orjson
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist, euclidean
from argparse import ArgumentParser

TEST_FILE="json/20220505_tilt_grid5_3_bulk_ribo_mmCpn1in4_3s_06_info.json"

p = ArgumentParser()
p.add_argument("-f", "--file", dest="filename", help="JSON file to load")
p.add_argument("-o", "--output", dest="output", help="Output filename for new JSON file")
p.add_argument("--inplace", dest="inplace", action="store_true", help="Replace the JSON file inplace (Danger)")
p.add_argument("-b", "--box", dest="box", action="append", help="Box to merge. Can provide multiple.")
p.add_argument("-l", "--label", dest="label", help="Label for new merged set")
p.add_argument("-d", "--min-distance", dest="mindist", default=100, help="Minimum distance between merged particles", type=float)
p.add_argument("--boxsz", dest="boxsize", help="Boxsize for new box set", type=int)
p.add_argument("-r", "--dry-run", dest="dryrun", action="store_true", help="Don't actually write the output")

args = vars(p.parse_args())

with open(args['filename'], 'rb') as f:
    data = orjson.loads(f.read())

merged = []
classes = {}
boxes = {}

for box in data['boxes_3d']:
    kid = box[5]
    name = data['class_list'][str(kid)]['name']

    if name not in boxes:
        boxes[name] = []

    boxes[name].append(box.copy())

for i,cls in data['class_list'].items():
    print("{}: {}".format(cls['name'], len(boxes[cls['name']])))

    classes[cls['name']] = cls

    if cls['name'] == args["label"]:
        print("ERROR: Target label already exists, won't overwrite")
        exit()

mindist = args['mindist'] / data['apix_unbin']

print()
print("Beginning merge run")
print("Target Label: {}".format(args['label']))
print("Distance cuttoff: {}".format(mindist))
print("Apix: {}".format(data['apix_unbin']))

for box_set in args['box']:
    print()
    print("Merging box {}".format(box_set))

    if box_set not in boxes:
        print("ERROR: Box {} is not present in this tomogram".format(box_set))
        print()
        exit()

    if len(merged) == 0:
        print("This is basis set: taking all {} boxes".format(len(boxes[box_set])))
        merged = boxes[box_set].copy()
        continue

    print("Merging {} boxes into {} already in new set.".format(len(boxes[box_set]), len(merged)))

    removed_count = 0
    for box in boxes[box_set]:
        # Oh yeah there's a better way to do this
        # Don't want to mess around with ndarrays, slicing and matrices yet though
        for other in merged:
            dist = euclidean(box[:3], other[:3])
            if (dist < mindist):
                removed_count += 1
                break
        else:
            merged.append(box.copy())

    print("Removed {} boxes for being below threshold {}".format(removed_count, args['mindist']))

print()
print("Creating new box set {} with {} boxes".format(args['label'], len(merged)))

new_id = len(data['class_list'])

boxsize = classes[args['box'][0]]['boxsize']
if args['boxsize'] is not None:
    boxsize = args['boxsize']

data['class_list'][str(new_id)] = {
    "boxsize": boxsize,
    "name": args["label"]
    }

for box in merged:
    box[5] = new_id

data['boxes_3d'].extend(merged)

if not args['dryrun']:
    with open(args['output'], 'wb') as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
