from testDefinitions.actionContext import ActionContext
from appController import LogMonitor
import asyncio
from playsound import playsound

async def MarkEvent(id : int,monitor : LogMonitor, context : ActionContext):
    if(context.awaitableEvents.get(id) is not None):
        context.awaitableEvents[id] = True
    else: 
        context.awaitableEvents[id] = True


async def Sleep(monitor : LogMonitor, context : ActionContext):
    #await for time
    await asyncio.sleep(5)

async def playSound(sound : str,monitor : LogMonitor,context : ActionContext):
    print(f"Playing sound {sound}")
    playsound(f"./sounds/{sound}")
    
def getActionMap():
    return {
        "MarkEvent": MarkEvent,
        "Sleep": Sleep,
        "PlaySound": playSound
    }