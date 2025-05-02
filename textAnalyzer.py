
from PIL import Image
import time
from transformers import pipeline
import torch


def analyzeText(deviceName,text_classifier,text,labels):
    deviceName = "/" + deviceName if deviceName is not "" else ""
    
    #results = model.predict(source=im1, save=True)  # type YOLONetResults
    
    outputs = text_classifier(text, labels)
    reformated_outputs = []

    for i in range(len(outputs['labels'])):
        reformated_outputs.append({"score": outputs['scores'][i], "label": outputs['labels'][i]})

    print(reformated_outputs)
    
    return reformated_outputs
    
    # for i in range(len(results)):
    #     print(results[i].names)
    #     print(results[i].tojson())
    # print(time.time() - timeToAnalyze)