import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import yaml
import time
from collections import defaultdict
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import datetime
import os
import numpy as np
import sys

# Simple hand data filter application to bit improve the quality of the data
# does need to have categories specified inside the code


categories = ["Advertisement"]

# Dropdown
# options = ["Náhodné tiktok účty",
# "Kosmetické výrobky", 
# "Obchody", 
# "Online akademie", 
# "Média", 
# "Snacky",
# "Finanční služby", 
# "Fast food", 
# "Automobilismus", 
# "Domácí spotřebiče", 
# "Videohry", 
# "Společenské události a místa", 
# "Zdraví",
# "Replastuj", 
# "Elektronika", 
# "Mazlíčci", 
# "Oblečení", 
# "Restaurace", 
# "Mobilní operátoři", 
# "Potraviny", 
# "Reality", 
# "Šperky", 
# "Aplikace", 
# "Asijská kultura", 
# "Cestování a hotely",
# "Nábytek",
# "Drogerie",
# "Práce a podezřelé nabídky",
# "Chyba"]

options = ["Stavba",
"Reality",
"Nábytek",
"Těžká technika",
"Auta",
"Půjčky a banky",
"Investice",
"Sázení",
"Obchody",
"Jídlo",
"Zdraví",
"Turismus",
"Zábava",
"Politika",
"Kosmetické výrobky",
"Zvířata",
"Industriální výrobky",
"Řešení pro firmy"]

# Handle the custom YAML tag
yaml.SafeLoader.add_constructor(
    'tag:yaml.org,2002:python/object/new:ActionContext.result',
    lambda loader, node: loader.construct_sequence(node)
)

fileName = ""
if len(sys.argv) > 1:
    fileName = sys.argv[1]
else:
    raise Exception("No file path provided")

timeSet = set()
#read the YAML data from a file
with open(fileName, 'r') as file:
    raw_data = yaml.safe_load(file)

print(len(raw_data))

measurementStart = raw_data[0][1]
missingResults = 0
totalResults = 0
measurementIndex = 0
imagesToAnalyze = []
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

    if entry[0] in categories:
        if not os.path.exists(f"./.cache/{entry[0]}-{ts}.png") and (entry[0] in categories):
            missingResults += 1
        else:
            imagesToAnalyze.append({"name": f"{entry[0]}-{ts}.png","measurementIndex":measurementIndex,"time":ts,"ExpectedLabel":entry[0]})
        totalResults += 1

    next_ts = next_entry[1]

    if ts + 4200 < next_ts:
        print(f"Measurement started at {datetime.datetime.fromtimestamp(measurementStart)} and ended at {datetime.datetime.fromtimestamp(ts)}.")
        print(f"Missing images {missingResults} out of {totalResults}")
        missingResults = 0
        totalResults = 0
        measurementIndex += 1
        measurementStart = next_ts
        # You can also add logic here to handle the gap, like filling it with zeros or interpolating





results_path = "./results/handFilteredResults.yaml"
folder_path = "./.cache/"


# Create window
root = tk.Tk()
root.title("Image Switcher")
# Image paths

def load_image(path):
    img = Image.open(path)
    img = img.resize((486, 945))
    return ImageTk.PhotoImage(img)

results = {}
totalCount = len(imagesToAnalyze)

photos = [load_image(os.path.join(folder_path,path["name"])) for path in imagesToAnalyze]
current_image = 0

# Show first image
img_label = tk.Label(root, image=photos[current_image])
img_label.pack(pady=10)

progress_label = tk.Label(root, text=f"Image {current_image + 1} of {totalCount}")
progress_label.pack(pady=10)




options.sort()
dropdown_var = tk.StringVar(value=options[0])
dropdown = ttk.Combobox(root, textvariable=dropdown_var, values=options)
dropdown.pack(pady=10)


def save_image_results():
    global current_image
    results[imagesToAnalyze[current_image]["name"]] = {
        "type":dropdown_var.get(),
        "time": time.ctime(float(imagesToAnalyze[current_image]["time"])),
        "measurementIndex":imagesToAnalyze[current_image]["measurementIndex"]
        }
    yaml.dump(results, open(results_path, "w"))
    print(f"Saved results for {imagesToAnalyze[current_image]['name']} with option {dropdown_var.get()}")

def moveToNextImage():
    global current_image
    current_image = (current_image + 1) % len(imagesToAnalyze)
    img_label.config(image=photos[current_image])
    img_label.image = photos[current_image]  # Keep a reference
    progress_label.config(text=f"Image {current_image + 1} of {totalCount}")

def switch_image():
    save_image_results()
    moveToNextImage()



# Button to switch image
btn = tk.Button(root, text="Save value", command=save_image_results)
btn.pack(pady=10)

# Button to switch image
btn1 = tk.Button(root, text="Skip image", command=moveToNextImage)
btn1.pack(pady=10)

# Button to switch image
btn2 = tk.Button(root, text="Save and continue", command=switch_image)
btn2.pack(pady=10)

root.mainloop()