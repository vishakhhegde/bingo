import numpy as np
import json
import os

import torch
import clip
from PIL import Image
from absl import app
from absl import flags

flags.DEFINE_string('dataset_json', None, 'JSON with dataset')
FLAGS = flags.FLAGS

TARGET_IMAGE_FOLDER = '/home/vishakh/bingo/src/boohoo/images'
TARGET_FEATURE_FOLDER = '/home/vishakh/bingo/src/boohoo/tmp'

class Model(object):
    def __init__(self):
        self.device = device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(
            "ViT-B/32", device=device)

    def get_image_features(self, image_path):
        image = self.preprocess(
            Image.open(image_path)).unsqueeze(0).to(self.device)	
        with torch.no_grad():
            image_features = self.model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features

    def get_text_features(self, text):
        text_tokenized = clip.tokenize([text]).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokenized)[0]
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features


def main(argv):
    del argv
    model = Model()
    with open(FLAGS.dataset_json, 'r') as f:
        all_data = json.load(f)
        all_image_features = {}
        for data in all_data:
            fname = None
            product_id = None
            title = None
            if 'product_id' in data and 'title' in data:
                product_id = data['product_id']
                title = data['title']
                fname = os.path.join(TARGET_IMAGE_FOLDER,
                                        "{}.jpg".format(product_id))
            if (fname and
                    product_id and
                    title and
                    os.path.isfile(fname)):
                image_features = model.get_image_features(fname)
                text_features = model.get_text_features(title)
                features = {}
                features['image_features'] = image_features.cpu().numpy().tolist()
                features['text_features'] = text_features.cpu().numpy().tolist()
                all_image_features[product_id] = features

    
    with open(os.path.join(TARGET_FEATURE_FOLDER, 'features.json'), 'w') as fout:
        json.dump(all_image_features, fout)


if __name__ == '__main__':
  app.run(main)