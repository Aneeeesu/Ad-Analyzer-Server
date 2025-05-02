import yaml
from collections import defaultdict
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import datetime
import os
import numpy as np

# Handle the custom YAML tag
yaml.SafeLoader.add_constructor(
    'tag:yaml.org,2002:python/object/new:ActionContext.result',
    lambda loader, node: loader.construct_sequence(node)
)

timeSet = set()
#read the YAML data from a file
with open('./mergedresults.yaml', 'r') as file:
    raw_data = yaml.safe_load(file)

print(len(raw_data))

measurementStart = raw_data[0][1]
missingResults = 0
totalResults = 0
for i in range(len(raw_data)):
    entry = raw_data[i]
    next_entry = raw_data[i+1] if i+1 < len(raw_data) else None
    if next_entry is None:
        ts = entry[1]
        print(f"Measurement started at {datetime.datetime.fromtimestamp(measurementStart)} and ended at {datetime.datetime.fromtimestamp(ts)}.")
        print(f"Missing images {missingResults} out of {totalResults}")
        print(f"End of data reached at entry {i}.")
        break
    
    if len(entry) < 2 or len(next_entry) < 2:
        print(f"Skipping entry {i} due to insufficient data")
        continue
    ts = entry[1]

    if entry[0] == "Ad" or entry[0] == "Advertisement":
        if not os.path.exists(f"./mergedImages/{entry[0]}-{ts}.png") and (entry[0] == "Ad" or entry[0] == "Advertisement"):
            missingResults += 1
        totalResults += 1

    next_ts = next_entry[1]

    if ts + 4200 < next_ts:
        print(f"Measurement started at {datetime.datetime.fromtimestamp(measurementStart)} and ended at {datetime.datetime.fromtimestamp(ts)}.")
        print(f"Missing images {missingResults} out of {totalResults}")
        missingResults = 0
        totalResults = 0
        measurementStart = next_ts
        # You can also add logic here to handle the gap, like filling it with zeros or interpolating