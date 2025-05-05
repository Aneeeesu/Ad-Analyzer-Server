import appController as ac
from testDefinitions.actionContext import ActionContext
from typing import Callable
from threading import Semaphore



class Event:
    triggerConditions : Callable[[ActionContext], bool]
    action : Callable[[...], None]
    action_args : list
    device : str | None
    def __init__(self):
        self.triggerConditions = None
        self.action = None
        self.action_args = []
        
    async def execute(self, monitor : ac.LogMonitor, context : ActionContext):
        self.action_args.append(monitor)
        self.action_args.append(context)
        print(self.action_args)
        await self.action(*self.action_args)