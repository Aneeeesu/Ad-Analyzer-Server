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
import traceback


# map of all possible actions
actionMap = {
    'TikTok': tiktok.getActionMap(),
    'NovinkyCZ': novinkyCZ.getActionMap(),
    'System': systemActions.getActionMap(),
    'Misc': miscActions.getActionMap(),
}






# Conditions
def percentage_condition(percentage : float,label :str, timeout : float, context : ActionContext):
    """
    This function was intended for usecase that never was actually used and may not work as expected.

    In reality the time that this would even need to be used is way longer than any realistic usecase.
    
    This condition checks if the average of the results is greater than the percentage.

    It is also fairly slow and not very efficient.
    Args:
        percentage (float): percentage to check
        label (str): label to check
        timeout (float): timeout in seconds
        context (ActionContext): context of the action
    Returns:
        bool: True if the average is greater than the percentage, False otherwise
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
    """
    This function checks if the event with the given id has been marked.
    Args:
        id (int): id of the event
        context (ActionContext): context of the action
    Returns:
        bool: True if the event has been marked, False otherwise
    """
    if(context.awaitableEvents.get(id) is not None):
        return context.awaitableEvents[id]
    else:
        context.awaitableEvents[id] = False
        return False
    

def timeout_condition(timeout : int, context : ActionContext):
    """
    This function checks if the timeout has been reached.
    Args:
        timeout (int): timeout in seconds
        context (ActionContext): context of the action
    Returns:
        bool: True if the timeout has been reached, False otherwise
    """
    return t.time() - context.start_timestamp > timeout

# map of all possible conditions
conditionMap = {
    'MarkEvent': (checkMarkEvent, [("Id",int)]),
    'Timeout': (timeout_condition,[("Timeout",int)]),
    'Percentage': (percentage_condition,[("Percentage",float),("Label",str),("Timeout",float)]),
}


def find_action(application: str, action: str):
    """
    Find the action in the action map.
    Args:
        application (str): The application name.
        action (str): The action name.
    Raises:
        Exception: If the application or action is not found.
    Returns:
        tuple: The action function and its supported arguments.
    """
    if actionMap.get(application) is None:
        raise Exception("Application not found")
    if actionMap.get(application).get(action) is None:
        raise Exception("Action not found")
    return actionMap[application][action]



def parse_condition(conditions: list[dict[str, any]]):
    """
    Parse conditions from description
    This function checks if the description contains a list of conditions and returns it.
    Args:
        conditions (list[dict[str, any]]): parsed conditions from yaml file
    Raises:
        Exception: Condition must contain type
        Exception: Condition type not found
        Exception: Condition argument must be of type
        Exception: Child conditions must be list
    Returns:
        _type_: Callable[[ActionContext], bool]: function that takes ActionContext and returns bool
    """
    possible_conditions = []

    for condition in conditions:
        # check if condition type is string
        if not isinstance(condition.get("Type"),str):
            raise Exception("Condition must contain type")
        
        condition_type = condition["Type"]

        # check if condition type is in conditionMap
        condition_mapped = conditionMap.get(condition_type)
        if condition_mapped is None:
            raise Exception(f"Condition {condition_type} not found")
        
        # get condition function and arguments
        condition_func = condition_mapped[0]
        condition_args = condition_mapped[1]

        # check if condition has all the args needed
        for arg in condition_args:
            if not isinstance(condition.get(arg[0]), arg[1]):
                raise Exception(f"Condition {condition_type} argument {arg[0]} must be {arg[1]}")
        #check if condition has child conditions 
        if condition.get("ChildConditions") is None:
            args = []
            for arg in condition_args:
                args.append(condition[arg[0]])
            possible_conditions.append(lambda x : condition_func(*args,x))
        # check if condition has child conditions and if they are in the right format
        elif isinstance(condition.get("ChildConditions"),list[dict[str, any]]):
            child_conditions = parse_condition(condition["ChildConditions"])
            possible_conditions.append(lambda x : condition_func(*args,x) and child_conditions(x))
        else:
            raise Exception("Child conditions must be list")

    return lambda x : any([condition(x) for condition in possible_conditions])


def parse_task(task_description : dict):
    """
    Parses task from description
    task format:
        Action: action name
        Application: application name
        Action_args: list of arguments for action
        Device: device name
        Conditions: list of conditions
    Args:
        task_description (dict): parsed task from yaml file
    """
    task = Task()
    
    # checks if action and application are strings
    if not isinstance(task_description.get("Action"), str):
        raise Exception("Task action name must be string")
    elif not isinstance(task_description.get("Application"), str):
        raise Exception("Task application must be string")

    # checks if action and application are in actionMap
    action_name = task_description["Action"]
    application =  task_description["Application"]
    action, supported_args = find_action(application,action_name)
    task.action = action
    task.device = task_description.get("Device")
    
    # checks if action_args is list and if it has the right length
    action_args = task_description.get("Action_args")
    if(action_args is None):
        action_args = []
    if(not isinstance(action_args, list)):
        action_args = [action_args]
        
    action_args_length = len(action_args)
    supported_args_len = len(supported_args)
    if action_args_length < supported_args_len:
        action_args += [None] * (supported_args_len - action_args_length)
    elif action_args_length > supported_args_len:
        raise Exception("Number of arguments does not match")
    else:
        for i in range(len(action_args)):
            if not isinstance(action_args[i], supported_args[i]):
                raise Exception("Argument type does not match")
            
        task.action_args = action_args
    
    # checks if conditions are list and if they are in the right format
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
    if description.get("Labels") is None or description.get("Labels") == []:
        return []
    elif not isinstance(description.get("Labels"),list):
        raise Exception("Labels need to be list")
    else:
        return description["Labels"]

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
    
    # check if file exists
    try:
        with open(fileName, 'r') as file:
            description = yaml.safe_load(file)
    except Exception as e:
        raise Exception(f"Error loading yaml file: {e}")

    # check if description is dictionary    
    if not isinstance(description,dict):
        raise Exception("yaml must be dictionary")
    
    # check if description contains all labels
    try:
        parsed_description.labels = parse_labels(description)
        parsed_description.adLabels = parse_ad_labels(description)
    except Exception as e:
        error_message += str(e)
        traceback.print_exc()
        
    
    # check if description contains tasks
    if not isinstance(description.get("Tasks"), list):
        error_message += "Description must contain list of Tasks\n"
    else:
        # parses all tasks
        for task in description["Tasks"]:
            try:
                parsed_description.tasks.append(parse_task(task))
            except Exception as e:
                traceback.print_exc()
                error_message += str(e)


    # check if all tasks have some device specified
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

    # check if description contains events
    if description.get("Events") is None:
        parsed_description.events = []
    elif not isinstance(description.get("Events"), list):
        error_message += "Description must contain list of Events\n"
    else:
        for event in description["Events"]:
            try:
                parsed_description.events.append(parse_event(event))
            except Exception as e:
                traceback.print_exc()
                error_message += str(e)

    # check for errors
    if(error_message != ""):
        raise Exception(error_message)
    return parsed_description