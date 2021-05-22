import numpy as np
import cv2
import csv
import json
import random

DATABASE_JSON = '/home/vishakh/bingo/src/boohoo/tmp/boohoo_tops.json'

def search(query_image_path):
    # image = cv2.imread(query_image_path)
    
    # At the moment, nothing is done with this image
    # We are going to return a random output.
    results = []
    with open(DATABASE_JSON, 'r') as fin:
        all_data = json.load(fin)
        results = random.sample(all_data, 12)

    return results