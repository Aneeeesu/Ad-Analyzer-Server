
from PIL import Image
import time
from transformers import pipeline
import torch


def analyzeImage(deviceName,image_classifier,imageName,labels):
    deviceName = "/" + deviceName if deviceName is not "" else ""
    
    im1 = Image.open(f"./.cache{deviceName}/{imageName}.png")
    
    outputs = image_classifier(im1, candidate_labels=labels)
    outputs = [{"score": round(output["score"], 4), "label": output["label"] } for output in outputs]
    print(image_classifier.device)
    
    print(outputs)
    
    return outputs
    
    # for i in range(len(results)):
    #     print(results[i].names)
    #     print(results[i].tojson())
    # print(time.time() - timeToAnalyze)