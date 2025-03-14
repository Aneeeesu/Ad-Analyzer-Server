import appController as ac
from appController import LogMonitor
import asyncio
from playsound import playsound
import random
import time as t
from time import sleep
from ActionContext import ActionContext

async def openDM(username : str, monitor : LogMonitor):
    await ac.broadcastAdb(
    "adb",
    f"shell am broadcast -a com.tenshite.inputmacros.TikTok.OpenDMs --es username '{username}'"
)

async def sendDM(message: str, monitor : LogMonitor):
    await ac.broadcastAdb("TikTok.SendDM","--es message ily",monitor)

async def goToHome(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.NavigateToHome","",monitor)
async def swipeDown(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.SwipeDown","",monitor)
async def swipeUp(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.SwipeUp","",monitor)
async def goToMessages(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.NavigateToMessages","",monitor)
async def goToProfile(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.NavigateToProfile","",monitor)
async def like(monitor : LogMonitor, context : ActionContext):
    await ac.broadcastAdb("TikTok.Like","",monitor)
    
def playSound(sound : str,monitor : ac.LogMonitor,context : ActionContext):
    print(f"Playing sound {sound}")
    playsound(f"./sounds/{sound}")


async def doomscroll(likedLabel : str,monitor : ac.LogMonitor, context : ActionContext):
    await goToHome(monitor)
    await swipeDown(monitor)
    timeStamp = t.time()
    filename = f"doomscroll-{timeStamp}"
    ac.takeScreenshot(filename)
    results = ia.analyzeImage(context.image_analyzer,filename,context.labels)
    #find first result that matches label
    result = next((result for result in results if result['label'] == likedLabel), None)
    if result is None:
        raise Exception("Labels do not match")
    if result['score'] > 0.9:
        await like(monitor)
    if result['score'] > 0.5 and random.random() > 0.5:
        sleep(abs(random.gauss(10,2)+5))
        
    context.add_result(results,timeStamp)