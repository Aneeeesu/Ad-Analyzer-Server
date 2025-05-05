import asyncio
from threading import Semaphore
from typing import Callable
from testDefinitions.actionContext import ActionContext
import appController as ac


class Task:
    action : Callable[[...], None]
    action_args : list
    mutex : Semaphore
    device : str | None
    
    # arg is TestFeedback and returns bool
    conditionsToStop : Callable[[ActionContext], bool] | None
    def __init__(self):
        self.mutex = Semaphore(1)
        self.conditionsToStop = None
        self.action = None
        self.action_args = []
        self.device = None
    
    async def __exec__(self):
        self.mutex.acquire()
        await self.action(*self.action_args)
        self.mutex.release()
        
    async def execute(self, monitor : ac.LogMonitor, context : ActionContext):
        self.action_args.append(monitor)
        self.action_args.append(context)
        if self.conditionsToStop is None:
            await context.execute_events(self.device,monitor,context)
            try:
                result = await asyncio.wait_for(self.__exec__(), timeout=300)  # Set timeout to 5 seconds
                print(result)
            except asyncio.TimeoutError:
                print("Task timed out and was skipped")
            return
        
        while not self.conditionsToStop(context):
            await context.execute_events(self.device,monitor,context)
            try:
                result = await asyncio.wait_for(self.__exec__(), timeout=300)  # Set timeout to 5 seconds
                print(result)
            except asyncio.TimeoutError:
                print("Task timed out and was skipped")
            
    def pause(self):
        self.mutex.acquire()
        
    def resume(self):
        self.mutex.release()