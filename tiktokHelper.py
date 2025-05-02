import appController as ac
from appController import LogMonitor
import asyncio
from playsound import playsound
import random
import time as t
from time import sleep
from actionContext import ActionContext
import imageAnalyzer as ia
import textAnalyzer as ta


async def openDM(username : str, monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.OpenDMs",f"--es username \\\"{username}\\\"".replace("'","\\\'"),monitor)


async def sendDM(message: str, monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.SendDM",f"--es message \\\"{message}\\\"".replace("'","\\\'"),monitor)


async def goToHome(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.NavigateToHome","",monitor)
async def swipeDown(monitor : LogMonitor, context : ActionContext):
    return await ac.broadcastAdb("TikTok.SwipeDown","",monitor)
async def swipeUp(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.SwipeUp","",monitor)
async def goToMessages(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.NavigateToMessages","",monitor)
async def goToProfile(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.NavigateToProfile","",monitor)
async def like(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.Like","",monitor)



async def Search(searchedText : str,monitor : ac.LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.Search",f"--es query {searchedText}",monitor)

    result = await swipeDown(monitor,context)
    contentType = result.split()[7]

    timeStamp = t.time()
    filename = f"{contentType}-{timeStamp}"
    filename = f"{result.split()[7]}-{timeStamp}"

    deviceName = monitor.deviceSelector.split()[1] if monitor.deviceSelector else ""
    ac.takeScreenshot(deviceName,filename)
    results = ia.analyzeImage(deviceName,context.image_analyzer,filename,context.labels)
    #find first result that matches label
    result = next((result for result in results if result['label'] == searchedText), None)

    if result is None:
        raise Exception("Labels do not match")
    if result['score'] > 0.9:
        await like(monitor,context)
    if result['score'] > 0.5 and random.random() > 0.5:
        sleep(abs(random.gauss(10,2)+5))

    context.add_result(contentType,results,timeStamp)

async def doomscroll(likedLabel : str,monitor : ac.LogMonitor, context : ActionContext):
    await goToHome(monitor,context)
    result = await swipeDown(monitor,context)
    timeStamp = t.time()
    contentType = result.split()[7]

    filename = f"{contentType}-{timeStamp}"

    deviceName = monitor.deviceSelector.split()[1] if monitor.deviceSelector else ""

    ac.takeScreenshot(deviceName,filename)
    results = {}

    #timeout

    
    description = " ".join(result.split()[7:])
    if contentType == "Ad":
        print(description)
        results = ta.analyzeText(deviceName,context.text_classifier,description,context.adLabels)
    else:
        results = ia.analyzeImage(deviceName,context.image_analyzer,filename,context.labels)
        #find first result that matches label
        result = next((result for result in results if result['label'] == likedLabel), None)
        if result is None:
            raise Exception("Labels do not match")
        if result['score'] > 0.9:
            await like(monitor,context)
        if result['score'] > 0.5 and random.random() > 0.5:
            sleep(abs(random.gauss(10,2)+5))
        
    context.add_result(contentType,results,timeStamp,description)


async def sendMessage(username:str,message:str,monitor : ac.LogMonitor,context : ActionContext):
    await openDM(username,monitor,context)
    await sendDM(message,monitor,context)