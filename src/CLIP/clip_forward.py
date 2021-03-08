import numpy as np
import json

import torch
import clip
from PIL import Image
from absl import app
from absl import flags

flags.DEFINE_string('input', None, 'Input Image')
flags.DEFINE_list('labels', [], 'A list of labels')
FLAGS = flags.FLAGS

class Model(object):
    def __init__(self):
        self.device = device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(
            "ViT-B/32", device=device)

    def process_input(self, image, labels):
        """Creates a probability distribution of image over labels.
        
        Args:
            image<str>: Path of the image to be processed.
            labels<list>: List of labels over which to predict.

        Returns:
            dict('probs', 'labels')
        """
        image = self.preprocess(
            Image.open(image)).unsqueeze(0).to(self.device)	
        text = clip.tokenize(labels).to(self.device)

        with torch.no_grad():
            image_features = self.model.encode_image(image)
            text_features = self.model.encode_text(text)
            
            logits_per_image, logits_per_text = self.model(image, text)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()
        
        probs = probs[0]
        output = {label: float(prob) for prob, label in zip(probs, labels)}

        return output

def main(argv):
    del argv
    model = Model()
    output = model.process_input(
        image=FLAGS.input,
        labels=FLAGS.labels)
    print(output)

if __name__ == '__main__':
  app.run(main)