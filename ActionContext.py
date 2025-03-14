from collections import namedtuple
from transformers import pipeline
import time as t

class ActionContext:
    time_before_step_start: float
    start_timestamp : float
    average_label_probability_in_last_hour : dict[str, float]
    labels : list[str]
    image_analyzer : pipeline
    result = namedtuple('result', ['timestamp','values'])
    
    results : list[result]
    
    def __init__(self,image_analyzer,labels):
        self.time_before_step_start = t.time()
        self.start_timestamp = t.time()
        self.average_label_probability_in_last_hour = {}
        self.image_analyzer = image_analyzer
        self.labels = labels
        self.results = []
    
    def add_result(self, new_result : list[tuple[str, float]],timeStamp : float):
        self.results.append(self.result(timeStamp,new_result))