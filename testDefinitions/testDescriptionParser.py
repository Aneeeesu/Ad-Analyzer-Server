import yaml
import appController as ac
import imageAnalyzer as ia
import time as t
from transformers import pipeline
from collections import namedtuple
from threading import Semaphore
from typing import Callable
from playsound import playsound
import random
from time import sleep
from testDefinitions.actionContext import ActionContext
from testDefinitions.task import Task
from testDefinitions.event import Event
import asyncio
import actionDescriptions.miscActions as miscActions
import actionDescriptions.tiktokActions as tiktok
import actionDescriptions.novinkyCZActions as novinkyCZ
import actionDescriptions.systemActions as systemActions
import warnings
from testDefinitions.description import Description



actionMap = {
    'TikTok': {
        tiktok.getActionMap()
    },

    'NovinkyCZ': {
        tiktok.getActionMap()
    },
    'System': {
        systemActions.getActionMap()
    },

    'Misc':{
        miscActions.getActionMap()
    }
}

def percentage_condition(percentage : float,label :str, timeout : float, context : ActionContext):
    """
    This function was intended for usecase that never was actually used and may not work as expected.
    
    This condition checks if the average of the results is greater than the percentage.
    """
    warnings.warn(
        "Percentage condition is deprecated and may not work as expected. ",
        DeprecationWarning,
        stacklevel=2
    )
    
    results = [result for result in context.results if t.time() - result.timestamp < timeout]
    if len(results) == 0:
        return False
    average = sum([result.values[label] for result in results])/len(results)
    return average > percentage

def checkMarkEvent(id : int, context : ActionContext):
    if(context.awaitableEvents.get(id) is not None):
        return context.awaitableEvents[id]
    else:
        context.awaitableEvents[id] = False
        return False
    

def timeout_condition(timeout : int, context : ActionContext):
    return t.time() - context.start_timestamp > timeout
    
    

    
async def sendDM(username : str, message : str, monitor : ac.LogMonitor,context : ActionContext):
    tiktok.openDM(username,monitor)
    tiktok.sendDM(message,monitor)

def find_action(application: str, action: str):
    if actionMap.get(application) is None:
        raise Exception("Application not found")
    if actionMap.get(application).get(action) is None:
        raise Exception("Action not found")
    return actionMap[application][action]

def is_mark_event_condition(condition : dict[str, any]):
    if not isinstance(condition.get("Type"),str):
        raise Exception("Condition must contain type")
    else:
        condition_type = condition["Type"]
        if condition_type == "MarkEvent":
            if not isinstance(condition.get("Id"), int):
                raise Exception("MarkEvent condition must contain id")
            else:
                return True
    return False

def is_timeout_condition(condition : dict[str, any]):
    if not isinstance(condition.get("Type"),str):
        raise Exception("Condition must contain type")
    else:
        condition_type = condition["Type"]
        if condition_type == "Timeout":
            if not isinstance(condition.get("Timeout"), int):
                raise Exception("Timeout condition must contain timeout")
            else:
                return True
    return False

def parse_condition(conditions: list[dict[str, any]]):
    possible_conditions = []

    for condition in conditions:
        if is_timeout_condition(condition):
            timeout = condition["Timeout"]
            if condition.get("ChildConditions") is None:
                possible_conditions.append(lambda x : timeout_condition(timeout, x))
            elif isinstance(condition.get("ChildConditions"),list[dict[str, any]]):
                child_conditions = parse_condition(condition["ChildConditions"])
                possible_conditions.append(lambda x : timeout_condition(timeout, x) and child_conditions(x))
            else:
                raise Exception("Child conditions must be list")
        elif is_mark_event_condition(condition):
            id = condition["Id"]
            if condition.get("ChildConditions") is None:
                possible_conditions.append(lambda x : checkMarkEvent(id,x))
            elif isinstance(condition.get("ChildConditions"),list[dict[str, any]]):
                child_conditions = parse_condition(condition["ChildConditions"])
                possible_conditions.append(lambda x : checkMarkEvent(id,x) and child_conditions(x))
            else:
                raise Exception("Child conditions must be list")
                
    
    return lambda x : any([condition(x) for condition in possible_conditions])


def parse_task(task_description : dict):
    task = Task()
    
    if not isinstance(task_description.get("Action"), str):
        raise Exception("Task action name must be string")
    elif not isinstance(task_description.get("Application"), str):
        raise Exception("Task application must be string")
    else:
        action_name = task_description["Action"]
        application =  task_description["Application"]
        action, supported_args = find_action(application,action_name)
        task.action = action
        task.device = task_description.get("Device")
    
    action_args = task_description.get("Action_args")
    if(action_args is None):
        action_args = []
    if(not isinstance(action_args, list)):
        action_args = [action_args]
        
    action_args_length = len(action_args)
    supported_args_len = len(supported_args)
    if action_args_length < supported_args_len:
        action_args += [None] * (supported_args_len - action_args_length)  # Efficient
    elif action_args_length > supported_args_len:
        raise Exception("Number of arguments does not match")
    else:
        for i in range(len(action_args)):
            if not isinstance(action_args[i], supported_args[i]):
                raise Exception("Argument type does not match")
            
        task.action_args = action_args
    
    if task_description.get("Conditions") is None:
        task.conditionsToStop = None
    elif not isinstance(task_description.get("Conditions"),list):
        raise Exception("Task conditions must be list")
    else:
        task.conditionsToStop = parse_condition(task_description["Conditions"])
    return task

        
        

def parse_labels(description : dict) -> list[str]:
    """
    Parse labels from description
    This function checks if the description contains a list of labels and returns it.
    Args:
        description (dict): parsed description from yaml file

    Raises:
        Exception: Description does not contain labels
        Exception: Labels are not list

    Returns:
        _type_: list[str]: list of labels
    """
    if description.get("Labels") is None:
        raise Exception("Description must contain list of labels")
    elif not isinstance(description.get("Labels"),list):
        raise Exception("Labels need to be list")
    else:
        labels = description["Labels"]
    
    return labels

def parse_ad_labels(description : dict):
    """
    Parse ad labels from description
    This function checks if the description contains a list of ad labels and returns it.
    Args:
        description (dict): parsed description from yaml file
    
    Raises:
        Exception: Description does not contain list of ad labels
        Exception: Ad labels are not list
    
    Returns:
        _type_: list[str]: list of ad labels
    """
    if description.get("AdLabels") is None:
        raise Exception("Description must contain list of ad labels")
    elif not isinstance(description.get("AdLabels"),list):
        raise Exception("AdLabels need to be list")
    else:
        labels = description["AdLabels"]
    
    return labels

def parse_event(event_description : dict):
    """
    Parses event from description
        Event format:
            TriggerConditions: list of conditions
            Action: action name
            Application: application name
            Action_args: list of arguments for action
            Device: device name
        
    Args:
        event_description (dict): parsed event from yaml file

    Raises:
        Exception: Task action name must be string
        Exception: Task application name must be string
        Exception: Task conditions must be list
        Exception: Task action args must be list
        Exception: Task action args must be string

    Returns:
        _type_: _description_
    """
    event = Event()
    
    if not isinstance(event_description.get("TriggerConditions"),list):
        raise Exception("Task conditions must be list")
    else:
        event.triggerConditions = parse_condition(event_description["TriggerConditions"])
    
    
    
    # checks if we can even parse action and application
    if not isinstance(event_description.get("Action"), str):
        raise Exception("Task action name must be string")
    elif not isinstance(event_description.get("Application"), str):
        raise Exception("Task application must be string")
    else:
        # checks if action and application are in actionMap
        action_name = event_description["Action"]
        action_args = event_description.get("Action_args")
        application =  event_description["Application"]
        action, supported_args = find_action(application,action_name)

        # checks if action_args is list and if it has the right length
        if(action_args is None):
            action_args = []
        if(not isinstance(action_args, list)):
            action_args = [action_args]
        
        action_args_length = len(action_args)
        supported_args_len = len(supported_args)
        # if there are not enough arguments, fill the rest with None
        if action_args_length < supported_args_len:
            action_args += [None] * (supported_args_len - action_args_length)
        # if there are too many arguments, raise exception
        if action_args_length > supported_args_len:
            raise Exception("Number of arguments does not match")
        # if there are the right number of arguments, check if the types match
        else:
            for i in range(len(action_args)):
                if not isinstance(action_args[i], supported_args[i]):
                    raise Exception("Argument type does not match")
        event.action = action
        event.action_args = action_args
        # gets the device from the description
        event.device = event_description.get("Device")
    return event
    

def load_description(fileName : str):
    """
    Load description from yaml file

    Args:
        fileName (str): name of the file to load

    Raises:
        Exception: Error loading yaml file
        Exception: yaml must be dictionary
        Exception: Description must contain list of Tasks

    Returns:
        _type_: Description: parsed instance of description
    """
    parsed_description = Description()
    error_message = ""
    
    try:
        with open(fileName, 'r') as file:
            description = yaml.safe_load(file)
    except Exception as e:
        raise Exception(f"Error loading yaml file: {e}")
        
    print(type(description))
    
    if not isinstance(description,dict):
        raise Exception("yaml must be dictionary")
    
    try:
        parsed_description.labels = parse_labels(description)
        parsed_description.adLabels = parse_ad_labels(description)
    except Exception as e:
        error_message += str(e)
        
    
    if not isinstance(description.get("Tasks"), list):
        error_message += "Description must contain list of Tasks\n"
    else:
        for task in description["Tasks"]:
            try:
                parsed_description.tasks.append(parse_task(task))
            except Exception as e:
                error_message += str(e)


    # check if there is any device that all tasks have some device specified
    if parsed_description.tasks is not None:
        all_tasks_have_device = True
        devices = []
        for task in parsed_description.tasks:
            if task.device is not None:
                if(task.device not in devices):
                    devices.append(task.device)
            else:
                all_tasks_have_device = False
        for task in parsed_description.events:
            if task.device is not None:
                if(task.device not in devices):
                    devices.append(task.device)
            else:
                all_tasks_have_device = False
        
        if all_tasks_have_device:
            parsed_description.devices = devices
        if all_tasks_have_device == False:
            error_message += "All tasks must have device\n"

    else:
        error_message += "Description must contain list of Tasks\n"

    if description.get("Events") is None:
        parsed_description.events = []
    elif not isinstance(description.get("Events"), list):
        error_message += "Description must contain list of Events\n"
    else:
        for event in description["Events"]:
            try:
                parsed_description.events.append(parse_event(event))
            except Exception as e:
                error_message += str(e)
    if(error_message != ""):
        raise Exception(error_message)
    return parsed_description