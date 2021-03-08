import json
from clarifai.apparel_detector import ApparelDetector

# URL = 'https://images.pexels.com/photos/458698/pexels-photo-458698.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940'
URL = '/home/vishakh/bingo/src/CLIP/examples/women_long_sweater.jpg'


if __name__ == '__main__':
    detector = ApparelDetector()
    response = detector.process_image(URL)
    
    for region in response.outputs[0].data.regions:
        if region.value > 0.85:
            label = region.data.concepts[0].name
            bounding_box = region.region_info.bounding_box
            x1 = bounding_box.top_row
            y1 = bounding_box.left_col
            x2 = bounding_box.bottom_row
            y2 = bounding_box.right_col
            bbox = [x1, y1, x2, y2]
            print(label, bbox, region.value)
