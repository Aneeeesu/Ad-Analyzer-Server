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
from transformers import AutoModel

from transformers import pipeline
from PIL import Image
from imageAnalyzer import analyzeImage
import os
import yaml
import sys
    

contentType = "AA"

def processEvent(line,semaphoreToRelease):
    tokens = line.split() # type: list[str]
    if(len(tokens) <= 6):
        return
    print(line)
    print(tokens[6])

    if(tokens[6].startswith("Content=")):
        global contentType
        contentType = tokens[6].split("=")[1]
        print(contentType)
        semaphoreToRelease.release()

async def main():
    description = load_description("test-description.yaml")
    image_classifier = pipeline(
    task="zero-shot-image-classification",
    model="laion/CLIP-ViT-H-14-laion2B-s32B-b79K",  # Replace with your chosen model
    device=0
    )
    os.makedirs(".cache", exist_ok=True)
    context = ActionContext(image_classifier,description.labels,description.events)
    

    semaphore = asyncio.Semaphore(1)
    monitor = LogMonitor("com.tenshite.inputmacros","AppControllerEvent", lambda x: processEvent(x,semaphore))
    monitor.start()
    
    for action in description.tasks:
        await action.execute(monitor,context)
    
    print(yaml.dump(context.results))

    monitor.stop()

if __name__ == "__main__":
   asyncio.run(main())
