import numpy as np
import cv2
import csv
import json
import random

from imagesearch_app.get_fashionpedia_attribute_logits import Model

DATABASE_JSON = '/home/vishakh/bingo/src/boohoo/tmp/boohoo_tops_new.json'
FEATURES_JSON = '/home/vishakh/bingo/src/boohoo/tmp/features_fashionpedia.json'

def search(query_image_path):
    model = Model()
    query_image_features = model.get_image_features(
        query_image_path)
    # At the moment, nothing is done with this image
    # We are going to return a random output.
    results = []
    searchable_data = {}
    with open(DATABASE_JSON, 'r') as fin:
        all_data = json.load(fin)
        for data in all_data:
            if 'product_id' in data:
                searchable_data[data['product_id']] = data

    with open(FEATURES_JSON, 'r') as fin:
        all_features = json.load(fin)
        similarity_scores = []
        for product_id, features in all_features.items():
            image_features = features['image_features']
            if image_features is not None:
                similarity_score = np.dot(
                    np.squeeze(image_features),
                    np.squeeze(query_image_features))
                similarity_scores.append((product_id, similarity_score))
        
        similarity_scores = sorted(similarity_scores,
                                   key=lambda x: x[1], reverse=True)
        top_12 = similarity_scores[:12]
        results = [searchable_data[product_id] for product_id, _ in top_12]
        # results = random.sample(all_data, 12)

    return results