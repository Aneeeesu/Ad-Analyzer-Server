import appController as ac
from testDefinitions.actionContext import ActionContext
from typing import Callable
from threading import Semaphore



class Event:
    """
    Class representing an event to be executed.
    Won't be interupted by other events.
    Attributes:
        triggerConditions (Callable): The conditions to trigger the event.
        action (Callable): The action to be executed.
        action_args (list): The arguments for the action.
        device (str | None): The device to execute the action on.
    """
    triggerConditions : Callable[[ActionContext], bool]
    action : Callable[[...], None]
    action_args : list
    device : str | None
    def __init__(self):
        """
        Initialize the Event object.
        """
        self.triggerConditions = None
        self.action = None
        self.action_args = []
        
    async def execute(self, monitor : ac.LogMonitor, context : ActionContext):
        """
        Execute the event with the provided monitor and context.
        Args:
            monitor (LogMonitor): The log monitor object.
            context (ActionContext): The action context object.
        """
        self.action_args.append(monitor)
        self.action_args.append(context)
        print(self.action_args)
        await self.action(*self.action_args)