import subprocess
import os
import uuid
from threading import Thread
import time
import asyncio
import select
from PIL import Image
from appController import LogMonitor
from appController import *
from imageAnalyzer import analyzeImage
from testDescriptionParser import load_description
from testDescriptionParser import ActionContext
from testDescriptionParser import Description
from transformers import AutoModel

from transformers import pipeline
from PIL import Image
from imageAnalyzer import analyzeImage
import os
import yaml
import sys


async def main():
    description = load_description("test-description.yaml")
    image_classifier = pipeline(
    task="zero-shot-image-classification",
    model="laion/CLIP-ViT-H-14-laion2B-s32B-b79K",  # Replace with your chosen model
    device=0
    )
    os.makedirs(".cache", exist_ok=True)
    context = ActionContext(image_classifier,description.labels,description.adLabels,description.events)
    deviceName = "8ad45a96"

    # read all existing screenshots
    screenshots = os.listdir(f"./.cache/{deviceName}")
    for screenshot in screenshots:
        if screenshot.endswith(".png") and screenshot.startswith("Ad-"):
            # remove the .png extension
            filename = os.path.splitext(screenshot)[0]
            # analyze the image
            results = analyzeImage(deviceName,image_classifier,filename,description.adLabels)
            # add the result to the context
            context.add_result("advertisment",results,filename)

    

            
    
    print(yaml.dump(context.results))
    # save the context to a YAML file
    with open(f"./results/results-{time.time()}.yaml", "w") as f:
        yaml.dump(context.results, f)


if __name__ == "__main__":
   asyncio.run(main())
