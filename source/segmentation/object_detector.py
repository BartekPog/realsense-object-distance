import os 

from pixellib.torchbackend.instance import instanceSegmentation


class ObjectDetector:
    def __init__(self):
        self.model = instanceSegmentation() # Init segmentation model
        dir_path = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(dir_path, "models/pointrend_resnet50.pkl")
        
        self.model.load_model(model_path)

    def segment_image(self, image):
        segmentation, segmentation_map = self.model.segmentFrame(image)

        return segmentation, segmentation_map