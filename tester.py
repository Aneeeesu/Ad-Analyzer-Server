import subprocess
import os
import uuid
from threading import Thread
from threading import Semaphore
import time
import asyncio
import select
from PIL import Image
from appController import LogMonitor
from appController import *
from imageAnalyzer import analyzeImage
from testDefinitions.testDescriptionParser import load_description
from testDefinitions.testDescriptionParser import ActionContext
from testDefinitions.testDescriptionParser import Description
from transformers import AutoModel

from transformers import pipeline
from PIL import Image
from imageAnalyzer import analyzeImage
from time import sleep
import os
import yaml
import sys
from time import sleep
from transformers import AutoTokenizer, AutoModelForSequenceClassification

timestamp = time.time()
# semaphore
fileSemaphore = Semaphore()


async def executeDeviceTasksAndEvents(device,description,monitor,context):
    """
    Execute the tasks and events for a given device.
    Args:
        device (str): The device to execute the tasks for.
        description (Description): The description object containing the tasks and events.
        monitor (LogMonitor): The log monitor object.
        context (ActionContext): The action context object.
    """
    tasks = description.getDeviceTasks(device)
        
    for action in tasks:
        # execute the action
        await action.execute(monitor,context)
        # wait a bit to improve stability
        sleep(1)
        fileSemaphore.acquire()
        sleep(0.5)
        # dump results to yaml file
        with open(f"./results/results-{timestamp}.yaml", "w") as f:
            yaml.dump(context.results, f)
        fileSemaphore.release()
        


async def main():
    # check if file name is passed as arg
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "test-description.yaml"
    
    #parse description file
    description = load_description(name)
    # prepare image classifier
    image_classifier = pipeline(
    task="zero-shot-image-classification",
    model="laion/CLIP-ViT-H-14-laion2B-s32B-b79K",  # Replace with your chosen model
    device=0
    )

    # prepare text classifier
    text_classifier = pipeline("zero-shot-classification",
                      model="joeddav/xlm-roberta-large-xnli")

    # make image output directories
    os.makedirs(".cache", exist_ok=True)
    
    # make device output directories
    for device in description.devices:
        os.makedirs(f".cache/{device}", exist_ok=True)
    
    # make results directory
    os.makedirs("results", exist_ok=True)
    context = ActionContext(image_classifier,text_classifier,description.labels,description.adLabels,description.events)
    



    # ensure there are devices in the description file    
    if description.devices is None:
        raise Exception("No devices found in description file")

    tasks = []
    for device in description.devices:
        # create a log monitor for each device
        monitor = LogMonitor("com.tenshite.inputmacros","AppControllerEvent",device)
        monitor.start()
        #create task for each device
        task = asyncio.create_task(executeDeviceTasksAndEvents(device,description,monitor,context))
        task.add_done_callback(lambda t: monitor.stop())
        
        tasks.append(task)
    #wait for all tasks to finish
    await asyncio.gather(*tasks)

    # dump results to yaml file    
    print(yaml.dump(context.results))
    with open(f"./results/results-{timestamp}.yaml", "w") as f:
        yaml.dump(context.results, f)


if __name__ == "__main__":
   asyncio.run(main())
