from collections import namedtuple
from transformers import pipeline
import time as t
from typing import Callable


class ActionContext:
    time_before_step_start: float
    start_timestamp : float
    average_label_probability_in_last_hour : dict[str, float]
    labels : list[str]
    image_analyzer : pipeline
    result = namedtuple('result', ['timestamp','values'])
    eventQueue : list

    events :list

    results : list[result]
    
    def __init__(self,image_analyzer,labels,events:list):
        self.time_before_step_start = t.time()
        self.start_timestamp = t.time()
        self.average_label_probability_in_last_hour = {}
        self.image_analyzer = image_analyzer
        self.labels = labels
        
        self.events = events 
        self.results = []
    
    def add_result(self, new_result : list[tuple[str, float]],timeStamp : float):
        self.results.append(self.result(timeStamp,new_result))

    async def execute_events(self,monitor,context):
        #check if any events are triggered
        for event in self.events:
            if event.triggerConditions(self):
                await event.execute(monitor,context)
                self.events.remove(event)