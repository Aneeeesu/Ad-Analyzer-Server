import yaml
from collections import defaultdict
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import datetime
import numpy as np
import seaborn as sns
import matplotlib.patches as patches
import time
import textwrap

#
# This file is just for generating graphs from the data
# It is not used in the main program
# It can be used but it does need code to be edited and I would more recommend visualizing the data in a different way
#


textIndexes = [1]

# Read the YAML data from a file
with open('./results/handFilteredResults.yaml', 'r') as file:
    raw_data = yaml.safe_load(file)

interesting_labels = None # ["Práce a podezřelé nabídky"]
date_format = "%a %b %d %H:%M:%S %Y"
interval = 600  # 300 seconds = 5 minutes

# First pass: collect all unique labels
labels = set()
for entry in raw_data:
    if raw_data[entry]["measurementIndex"] in textIndexes:
        if interesting_labels is None or raw_data[entry]["type"] in interesting_labels:
            labels.add(raw_data[entry]["type"])
        else:
            labels.add("Ostatní")

# Second pass: group data by time intervals
grouped_data = defaultdict(lambda: defaultdict(list))  # {rounded_timestamp: {label: [scores]}}

for entry in raw_data:
    if raw_data[entry]["measurementIndex"] not in textIndexes:
        continue
        
    rounded_ts = int(time.mktime(time.strptime(raw_data[entry]["time"], date_format)) // interval * interval)
    
    if interesting_labels is not None and raw_data[entry]["type"] not in interesting_labels:
        label = "Ostatní"
    else:
        label = raw_data[entry]["type"]
    grouped_data[rounded_ts][label].append(1)  # Using 1 for presence, 0 for absence

# Prepare data for plotting
time_points = []
averaged_scores = {label: [] for label in labels}

for rounded_ts in sorted(grouped_data.keys()):
    time_points.append(datetime.datetime.fromtimestamp(rounded_ts))
    current_data = grouped_data[rounded_ts]
    
    for label in labels:
        if label in current_data:
            # Calculate average presence for this label in this time interval
            averaged_scores[label].append(sum(current_data[label]))
        else:
            averaged_scores[label].append(0)

# Data preparation for heatmap
heatmap_data = []
#for more consistency
labels_list = list(labels) 

for label in labels_list:
    heatmap_data.append(averaged_scores[label])


heatmap_array = np.array(heatmap_data).T 

# Vykresli heatmapu
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_array.T, xticklabels=time_points, yticklabels=['\n'.join(textwrap.wrap(label, width=20)) for label in labels_list], cmap="YlOrRd", cbar=False,annot=True)


first = True
for i in range(len(time_points)):
    if i+1 < len(time_points):
        if time_points[i+1] - time_points[i] > datetime.timedelta(seconds=interval):
            if first:
                plt.axvline(i+1, color='cyan', linestyle='--', linewidth=2, label="Pauza v měření")
                first = False
            else:
                plt.axvline(i+1, color='cyan', linestyle='--', linewidth=2)


# plt.axvline(0, color='cyan', linestyle='--', linewidth=2, label="Konverzace")
# plt.axvline(12, color='cyan', linestyle='--', linewidth=2)
    


plt.title(f"Heatmapa výskytu reklam podle kategorie ({int(interval/60)}min intervaly)")
plt.xlabel("Čas")
plt.ylabel("Kategorie")
plt.xticks(rotation=45,ticks=range(0, len(time_points), 1), labels=[t.strftime('%H:%M') for i, t in enumerate(time_points)])
plt.tight_layout()
plt.legend()
plt.show()



def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{v:d}'.format(v=val)
    return my_autopct

# Adding sums to the labels
total_counts = {label: sum(averaged_scores[label]) for label in labels}

# Data preparation for bar graphs
labels_list = list(total_counts.keys())
sizes = list(total_counts.values())

sorted_data = sorted(zip(sizes, labels_list), reverse=True)
sorted_sizes, sorted_labels = zip(*sorted_data)

plt.figure(figsize=(10, len(sorted_labels) * 0.4))
bars = plt.barh(range(len(sorted_labels)), sorted_sizes, color='steelblue')
plt.yticks(range(len(sorted_labels)), sorted_labels,fontsize=12)
plt.xlabel("Počet výskytů")
plt.title("Podíl kategorií reklam během experimentu")

# Add values to end of bars
for i, v in enumerate(sorted_sizes):
    plt.text(v + 1, i, str(v), va='center')

plt.tight_layout()
plt.show()



# Preparing data
all_experiments = set(raw_data[entry]["measurementIndex"] for entry in raw_data)

experiment_totals = defaultdict(lambda: defaultdict(int))

for entry in raw_data:
    measurement_index = raw_data[entry]["measurementIndex"]
    label = raw_data[entry]["type"] if raw_data[entry]["type"] in interesting_labels else "Ostatní"
    experiment_totals[measurement_index][label] += 1

# Sorting experiments
sorted_experiments = sorted(experiment_totals.keys())

# Preparing data for stacked bar graph
labels_list = interesting_labels + ["Ostatní"]
stack_data = {label: [] for label in labels_list}

for experiment in sorted_experiments:
    for label in labels_list:
        stack_data[label].append(experiment_totals[experiment].get(label, 0))

# Plotting stacked bar graph
plt.figure(figsize=(12, 6))

bottom = np.zeros(len(sorted_experiments))

for label in labels_list:
    values = stack_data[label]
    plt.bar(sorted_experiments, values, bottom=bottom, label=label)
    bottom += values

plt.title('Počet reklam podle kategorie napříč experimenty')
plt.xlabel('Index experimentu')
plt.ylabel('Počet reklam')
plt.legend()
plt.tight_layout()
plt.show()
