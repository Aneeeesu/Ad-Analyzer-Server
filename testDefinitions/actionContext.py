from collections import namedtuple
from transformers import pipeline
import time as t
from typing import Callable


class ActionContext:
    """
    Class representing the context of an action.
    Attributes should not need to be changed from outside the class.
    """
    time_before_step_start: float
    start_timestamp : float
    labels : list[str]
    image_analyzer : pipeline
    result = namedtuple('result', ['type','timestamp','values','description'])
    awaitableEvents : dict[int,bool] = {}
    eventQueue : list

    events :list

    results : list[result]
    
    def __init__(self,image_analyzer,text_classifier,labels,adLabels,events:list):
        self.time_before_step_start = t.time()
        self.start_timestamp = t.time()
        self.image_analyzer = image_analyzer
        self.labels = labels
        self.adLabels = adLabels
        self.text_classifier = text_classifier        
        self.events = events 
        self.results = []
    
    def add_result(self,type : str, new_result : list[tuple[str, float]],timeStamp : float,description : str = ""):
        """
        Add a result to the context.
        Args:
            type (str): The type of the result.
            new_result (list[tuple[str, float]]): The result data.
            timeStamp (float): The timestamp of the result.
            description (str): A description of the result.
        """
        self.results.append(self.result(type,timeStamp,new_result,description))

    async def execute_events(self,device,monitor,context):
        """
        Execute the events for a given device.
        Args:
            device (str): The device to execute the events for.
            monitor (LogMonitor): the device log monitor.
            context (ActionContext): The experiment context.
        """
        #check if any events are triggered
        for event in self.events:
            if event.device == device and event.triggerConditions(self):
                await event.execute(monitor,context)
                self.events.remove(event)