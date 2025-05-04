import yaml
from collections import defaultdict
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import datetime
import numpy as np

# Handle the custom YAML tag
yaml.SafeLoader.add_constructor(
    'tag:yaml.org,2002:python/object/new:ActionContext.result',
    lambda loader, node: loader.construct_sequence(node)
)


#read the YAML data from a file
with open('./results/results-1744816598.7336326.yaml', 'r') as file:
    raw_data = yaml.safe_load(file)



# Group scores into 10-minute intervals
interval = 300  # 600 seconds = 10 minutes
grouped_data = defaultdict(lambda: defaultdict(list))  # {rounded_timestamp: {label: [scores]}}

for entry in raw_data:
    kind, ts, labels,description = entry
    if kind != "Ad":
        continue

    rounded_ts = int(ts // interval * interval)

    for label_score in labels:
        label = label_score["label"]
        score = label_score["score"]
        grouped_data[rounded_ts][label].append(score)

# Now average them
averaged_scores = defaultdict(list)  # {label: [avg_score]}
time_points = []

for rounded_ts in sorted(grouped_data.keys()):
    time_points.append(datetime.datetime.fromtimestamp(rounded_ts))
    label_scores = grouped_data[rounded_ts]

    # Collect average score per label
    for label, scores in label_scores.items():
        for i in range(len(scores)):
            scores[i] = scores[i] if scores[i] > 0.5 else 0
        averaged_scores[label].append(sum(scores) / len(scores))


    # For missing labels in this time slot, append 0 to keep lines continuous
    all_labels = set(averaged_scores.keys())
    current_labels = set(label_scores.keys())
    for label in all_labels - current_labels:
        averaged_scores[label].append(0.0)


# Prepare the data for stackplot (stacking each label's scores)
scores_to_stack = [averaged_scores[label] for label in averaged_scores]

bottom = np.zeros(len(scores_to_stack[0]))  # Initialize bottom for stacking

# Plotting
plt.figure(figsize=(12, 6))
#plt.stackplot(time_points, *scores_to_stack, labels=averaged_scores.keys(), alpha=0.5)

color_palette = plt.cm.get_cmap('tab20', len(averaged_scores))  # Using 'tab20' colormap, change to suit your needs
colors = [color_palette(i) for i in range(len(averaged_scores))]

for label,scores in averaged_scores.items():
    plt.bar(time_points, scores,width= 0.001, bottom=bottom,label=label,color=colors.pop(0))
    bottom += scores

plt.title("Ad Category Score Trends (10-Minute Averages)")
plt.legend(loc='upper left', reverse=True)
plt.xlabel("Time")
plt.ylabel("Average Score")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True)
plt.show()