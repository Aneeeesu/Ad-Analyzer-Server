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

#
async def executeDeviceTasksAndEvents(device,description,monitor,context):
    if device is None:
        tasks = description.tasks
    else:
        tasks = description.getDeviceTasks(device)
        
    for action in tasks:
        await action.execute(monitor,context)
        sleep(1)
        fileSemaphore.acquire()
        sleep(0.5)
        with open(f"./results/results-{timestamp}.yaml", "w") as f:
            yaml.dump(context.results, f)
        fileSemaphore.release()
        

# take name as arg
async def main():
    # check if name is passed as arg
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "test-description.yaml"
    
    description = load_description(name)
    image_classifier = pipeline(
    task="zero-shot-image-classification",
    model="laion/CLIP-ViT-H-14-laion2B-s32B-b79K",  # Replace with your chosen model
    device=0
    )

    text_classifier = pipeline("zero-shot-classification",
                      model="joeddav/xlm-roberta-large-xnli")

    os.makedirs(".cache", exist_ok=True)
    
    for device in description.devices:
        os.makedirs(f".cache/{device}", exist_ok=True)
    
    os.makedirs("results", exist_ok=True)
    context = ActionContext(image_classifier,text_classifier,description.labels,description.adLabels,description.events)
    



    
    if description.devices is None:
        monitor = LogMonitor("com.tenshite.inputmacros","AppControllerEvent")
        monitor.start()
        for action in description.tasks:
            await executeDeviceTasksAndEvents(None,description,monitor,context)
        monitor.stop()
    else:
        tasks = []
        for device in description.devices:
            monitor = LogMonitor("com.tenshite.inputmacros","AppControllerEvent",device)
            monitor.start()
            #create task for each device
            # await executeDeviceTasksAndEvents(device,description,monitor,context)
            task = asyncio.create_task(executeDeviceTasksAndEvents(device,description,monitor,context))
            task.add_done_callback(lambda t: monitor.stop())
            
            tasks.append(task)
        #wait for all tasks to finish
        await asyncio.gather(*tasks)
    #wait for semaphore to be released

            
    
    print(yaml.dump(context.results))
    with open(f"./results/results-{timestamp}.yaml", "w") as f:
        yaml.dump(context.results, f)


if __name__ == "__main__":
   asyncio.run(main())
