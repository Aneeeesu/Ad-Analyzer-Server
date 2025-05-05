import asyncio
from threading import Semaphore
from typing import Callable
from testDefinitions.actionContext import ActionContext
import appController as ac


class Task:
    """
    Class representing a task to be executed
    Attributes:
        action (Callable): The action to be executed.
        action_args (list): The arguments for the action.
        mutex (Semaphore): A semaphore for thread synchronization.
        device (str | None): The device to execute the action on.
        conditionsToStop (Callable | None): A condition to determine if the task should stop.
    """
    action : Callable[[...], None] # action is a function that takes LogMonitor and ActionContext as arguments
    action_args : list # arguments for the action
    mutex : Semaphore # semaphore for thread synchronization
    device : str | None # device to execute the action on
    
    # arg is TestFeedback and returns bool
    conditionsToStop : Callable[[ActionContext], bool] | None
    def __init__(self):
        """
        Initialize the Task object.
        """
        self.mutex = Semaphore(1)
        self.conditionsToStop = None
        self.action = None
        self.action_args = []
        self.device = None
    
    async def __exec__(self):
        """
        Execute the action with the provided arguments.
        Locks the mutex.
        """
        self.mutex.acquire()
        await self.action(*self.action_args)
        self.mutex.release()
        
    async def execute(self, monitor : ac.LogMonitor, context : ActionContext):
        """
        Execute the task with the provided monitor and context.
        Args:
            monitor (LogMonitor): The log monitor object.
            context (ActionContext): The action context object.
        """
        self.action_args.append(monitor)
        self.action_args.append(context)
        # if condtionless execute once
        if self.conditionsToStop is None:
            # first check and execute events
            await context.execute_events(self.device,monitor,context)
            try:
                # execute with timeout
                result = await asyncio.wait_for(self.__exec__(), timeout=300)  # Set timeout to 5 seconds
                print(result)
            except asyncio.TimeoutError:
                print("Task timed out and was skipped")
            return
        
        # if condition is set, execute until condition is met
        while not self.conditionsToStop(context):
            await context.execute_events(self.device,monitor,context)
            try:
                # execute with timeout
                result = await asyncio.wait_for(self.__exec__(), timeout=300)  # Set timeout to 5 seconds
                print(result)
            except asyncio.TimeoutError:
                print("Task timed out and was skipped")
            
    def pause(self):
        """
        Pause the task by acquiring the mutex.
        """
        self.mutex.acquire()
        
    def resume(self):
        """
        Resume the task by releasing the mutex.
        """
        self.mutex.release()