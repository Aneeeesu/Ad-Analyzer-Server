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
    while result.split()[7] == "true":
        timeStamp = t.time()
        filename = f"Advertisement-{timeStamp}"
        ac.takeScreenshot(filename)
        results = ia.analyzeImage(context.image_analyzer,filename,context.labels)
        context.add_result("advertisment",results,timeStamp)

        result = await ac.broadcastAdb("NovinkyCZ.FocusAd","",monitor)


async def Open(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("NovinkyCZ.Open","",monitor)
    sleep(10)