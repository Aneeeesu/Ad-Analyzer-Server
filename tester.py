import subprocess
import os
import uuid
from threading import Thread
import time
import asyncio
import select
import cv2
from PIL import Image
from ultralytics import YOLO 
from appController import LogMonitor
from appController import *
from imageAnalyzer import analyzeImage
from testDescriptionParser import load_description
from testDescriptionParser import ActionContext
from transformers import AutoModel

from transformers import pipeline
from PIL import Image
import requests
from imageAnalyzer import analyzeImage
    

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
    context = ActionContext(image_classifier,description.labels)
    

    semaphore = asyncio.Semaphore(1)
    monitor = LogMonitor("com.tenshite.inputmacros","AppControllerEvent", lambda x: processEvent(x,semaphore))
    monitor.start()
    
    for action in description.tasks:
        await action.execute(monitor,context)
    
    # # await broadcastAdb("TikTok.OpenDMs","--es username aneeeesu",monitor)
    # # print("DMs opened")
    # # await broadcastAdb("TikTok.SendDM","--es message ily",monitor)
    # print("Message sent")
    # await broadcastAdb("TikTok.NavigateToHome","",monitor)
    
    # contentTypeCounter = {}
    # global contentType
    # await broadcastAdb("TikTok.SwipeDown","",monitor)
    # while(True):
    #     await semaphore.acquire()
    #     if contentType not in contentTypeCounter:
    #         contentTypeCounter[contentType] = 0
    #     takeScreenshot(f"{contentType}-{str(contentTypeCounter[contentType])}")
    #     analyzeImage(image_classifier,f"{contentType}-{str(contentTypeCounter[contentType])}")
    #     contentTypeCounter[contentType] += 1
    #     await broadcastAdb("TikTok.SwipeDown","",monitor)

if __name__ == "__main__":
   asyncio.run(main())
