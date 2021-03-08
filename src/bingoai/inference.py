import os

from CLIP.clip_forward import Model

ALL_LABELS = ["shorts",
              "jacket",
              "sweater",
              "shoes",
              "shirt",
              "long pants",
              "backpack",
              "sunglasses"]

class InferencePipeline(object):
    def __init__(self):
        self.model = Model()

    def process_input(self, input):
        output = self.model.process_input(
            image=input['image'],
            labels=input['labels'])

        return output