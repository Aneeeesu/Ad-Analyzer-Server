from testDefinitions.task import Task
from testDefinitions.event import Event

class Description:
    labels : list[str]
    adLabels : list[str]
    tasks : list[Task]
    events : list[Event]
    devices : list[str]
    def __init__(self):
        self.labels = []
        self.tasks = []
        self.events = []
        self.adLabels = []
    def getDeviceTasks(self,device : str):
        tasks = []
        for task in self.tasks:
            if task.device == device:
                tasks.append(task)
        return tasks
    
    def getDeviceEvents(self,device : str):
        events = []
        for event in self.events:
            if event.device == device:
                events.append(event)
        return events