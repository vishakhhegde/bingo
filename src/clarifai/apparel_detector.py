import os
import json
import validators

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2

stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())

URL = 'https://images.pexels.com/photos/458698/pexels-photo-458698.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940'

class ApparelDetector(object):
    def __init__(self):
        # This is how you authenticate.
        self.metadata = (('authorization', 'Key ea23ac20b84b480999b44c1bd87e9413'),)
        self.model_id = '72c523807f93e18b431676fb9a58e6ad'
    
    def process_image(self, image_path):
        is_valid_url = validators.url(image_path)
        if is_valid_url:
            request = service_pb2.PostModelOutputsRequest(
                # This is the model ID of a publicly available General model. You may use any other public or custom model ID.
                model_id=self.model_id,
                inputs=[
                resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(url=image_path)))
                ])
        elif os.path.isfile(image_path):
            with open(image_path, "rb") as f:
                file_bytes = f.read()
            request = service_pb2.PostModelOutputsRequest(
                # This is the model ID of a publicly available General model. You may use any other public or custom model ID.
                model_id=self.model_id,
                inputs=[
                resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(base64=file_bytes)))
                ])
        else:
            raise ValueError('image_path: {} does not exist'.format(image_path))

        response = stub.PostModelOutputs(request, metadata=self.metadata)

        if response.status.code != status_code_pb2.SUCCESS:
            raise Exception("Request failed, status code: " + str(response.status.code))

        else:
            return response

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