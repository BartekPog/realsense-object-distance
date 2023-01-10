
import os 
from datetime import datetime

import matplotlib.pyplot as plt 


from depth import DepthCameraClient
from processing_nodes import ProcessingNode
from segmentation import ObjectDetector

from rosbridge_json_connector import RosbridgeJSONConnector, RosClientDisconnected



class ProcessingPipeline:
    def __init__(self, host='192.168.0.150', port=9090, segmentation_image_path: str = None):
        self.rosbridge_connector = RosbridgeJSONConnector()

        self.camera_client = DepthCameraClient()

        self.processing_nodes = [
            node_class()
            for node_class in ProcessingNode.__subclasses__()
            if node_class.active
        ]

        print(f"DEBUG subclasses: {ProcessingNode.__subclasses__()}")
        
        self.rosconnector_node_pairs = [
            (RosbridgeJSONConnector(host=host, port=port, topic=node.target_topic), node)
            for node in self.processing_nodes
        ]

        self.requires_segmentation = any([node.requires_segmentation for node in self.processing_nodes])

        self.object_detector = None

        if self.requires_segmentation:
            self.object_detector = ObjectDetector()

        if not os.path.exists(segmentation_image_path):
            os.makedirs(segmentation_image_path)

        self.segmentation_image_path = segmentation_image_path
        
        
    def save_segmentation_map(self, segmentation_image):

        datetime_text = datetime.now().strftime(r'%Y-%m-%d--%H-%M-%S')
        
        file_name = f'segmentation_{datetime_text}.png'
        image_path = os.path_join(self.segmentation_image_path, file_name)

        plt.imsave(image_path, segmentation_image)


    def publish_iteration(self) -> list:

        depth_image, color_image, color_frame  = self.camera_client.get_aligned_images()

        segmented_image = None

        if self.requires_segmentation:
            segmented_image, segmentation_map = ObjectDetector.segment_image(color_image)

            if self.segmentation_image_path is not None:
                self.save_segmentation_map(segmentation_map) 


        for rosconnector, node in self.rosconnector_node_pairs:
            result_values = node.get_iteration_results(depth_image, color_image, color_frame, segmented_image)
            rosconnector.publish_message(result_values)

    
if __name__ == "__main__":
    pipeline = ProcessingPipeline(host='192.168.0.150', segmentation_image_path='./segmentation-images')

    try:
        while True:
            pipeline.publish_iteration()

    except RosClientDisconnected as e:
        print(f"RosClient error: {e}")