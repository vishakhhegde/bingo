import os
import cv2
import json

from absl import app
from absl import flags

flags.DEFINE_string('input', None, 'Input Image')
FLAGS = flags.FLAGS

def click_event(event, x, y, flags, params): 
    if event == cv2.EVENT_LBUTTONDOWN: 
        font = cv2.FONT_HERSHEY_SIMPLEX
        img = params['image']
        keypoints = params['keypoints']
        cv2.putText(img, str(x) + ',' +
                    str(y), (x,y), font, 
                    0.5, (0, 150, 255), 1) 
        cv2.imshow('image', img)
        keypoints.append((x, y))

def get_keypoints(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (640, 480))
    cv2.imshow('image', img)
    keypoints = []
    params = {
        'image': img,
        'keypoints': keypoints,
    }
    cv2.setMouseCallback('image', click_event, params)
    while True:
        if cv2.waitKey(20) and len(keypoints) >= 14:
            break
    cv2.destroyAllWindows()
    return keypoints

def main(argv):
    del argv
    keypoints = get_keypoints(FLAGS.input)
    json_output = {
        'keypoints': keypoints,
    }
    output_filename = os.path.splitext(FLAGS.input)[0] + '.json'
    with open(output_filename, 'w') as fout:
        json.dump(json_output, fout)

if __name__=="__main__": 
    app.run(main)