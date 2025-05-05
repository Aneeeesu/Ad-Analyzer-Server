
from PIL import Image
import time
from transformers import pipeline
import torch


def analyzeImage(deviceName,image_classifier,imageName,labels):
    """
    Analyze an image using a zero-shot image classification model.
    Args:
        deviceName (str): The name of the device.
        image_classifier (pipeline): The zero-shot image classification pipeline.
        imageName (str): The name of the image file to analyze.
        labels (list): A list of candidate labels for classification.
    Returns:
        list: A list of dictionaries containing the classification results.
    """
    if deviceName == "":
        raise Exception("Device name is empty")
    
    im1 = Image.open(f"./.cache{deviceName}/{imageName}.png")
    
    outputs = image_classifier(im1, candidate_labels=labels)
    outputs = [{"score": round(output["score"], 4), "label": output["label"] } for output in outputs]
    print(image_classifier.device)
    
    print(outputs)
    
    return outputs
