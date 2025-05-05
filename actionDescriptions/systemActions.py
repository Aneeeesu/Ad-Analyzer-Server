from testDefinitions.actionContext import ActionContext
from appController import LogMonitor
from appController import broadcastAdb

async def wakeUp(monitor : LogMonitor, context : ActionContext):
    await broadcastAdb("wakeup","",monitor)

def getActionMap():
    return {
        "WakeUp": (wakeUp,[])
    }