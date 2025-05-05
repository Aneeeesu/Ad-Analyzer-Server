
from PIL import Image
import time
from transformers import pipeline
import torch


def analyzeText(deviceName,text_classifier,text,labels):
    """
    Analyze text using a zero-shot text classification model.
    Args:
        deviceName (str): The name of the device.
        text_classifier (pipeline): The zero-shot text classification pipeline.
        text (str): The text to analyze.
        labels (list): A list of candidate labels for classification.
    Returns:
        list: A list of dictionaries containing the classification results.
    """
    deviceName = "/" + deviceName if deviceName is not "" else ""
    
    #results = model.predict(source=im1, save=True)  # type YOLONetResults
    
    outputs = text_classifier(text, labels)
    reformated_outputs = []

    # Reformat the outputs to match the image classifier format
    for i in range(len(outputs['labels'])):
        reformated_outputs.append({"score": outputs['scores'][i], "label": outputs['labels'][i]})

    print(reformated_outputs)
    
    return reformated_outputs
