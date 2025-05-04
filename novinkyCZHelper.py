import appController as ac
from appController import LogMonitor
import asyncio
from playsound import playsound
import random
import time as t
from time import sleep
from ActionContext import ActionContext
import imageAnalyzer as ia


async def go_trough_ads(monitor : LogMonitor, context : ActionContext):
    result = await ac.broadcastAdb("NovinkyCZ.FocusAd","",monitor)
    print(result.split()[7] == "true")
    while result.split()[7] == "true":
        timeStamp = t.time()
        print("time")
        filename = f"Advertisement-{timeStamp}"
        ac.takeScreenshot(monitor.deviceSelector.split()[1],filename)
        print("screen")
        results = ia.analyzeImage(monitor.deviceSelector.split()[1],context.image_analyzer,filename,context.labels)
        context.add_result("advertisment",results,timeStamp)

        result = await ac.broadcastAdb("NovinkyCZ.FocusAd","",monitor)


async def Open(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("NovinkyCZ.Open","",monitor)
    sleep(10)