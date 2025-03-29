import asyncio
from threading import Semaphore
from typing import Callable
from ActionContext import ActionContext
import appController as ac


class Task:
    action : Callable[[...], None]
    action_args : list
    mutex : Semaphore
    
    # arg is TestFeedback and returns bool
    conditionsToStop : Callable[[ActionContext], bool] | None
    def __init__(self):
        self.mutex = Semaphore(1)
        self.conditionsToStop = None
        self.action = None
        self.action_args = []
    
    async def __exec__(self):
        self.mutex.acquire()
        await self.action(*self.action_args)
        self.mutex.release()
        
    async def execute(self, monitor : ac.LogMonitor, context : ActionContext):
        self.action_args.append(monitor)
        self.action_args.append(context)
        if self.conditionsToStop is None:
            await context.execute_events(monitor,context)
            await self.__exec__()
            return
        
        while not self.conditionsToStop(context):
            await context.execute_events(monitor,context)
            await self.__exec__()
            
    def pause(self):
        self.mutex.acquire()
        
    def resume(self):
        self.mutex.release()