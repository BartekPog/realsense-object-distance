import abc

class ProcessingNode(abc.ABC):
    target_topic = "override_in_subclass"
    requires_segmentation = False
    active = True

    def __init__(self):
        print(f"Initiated node {self.__class__.__name__} with topic {self.target_topic}")


    @abc.abstractmethod
    def get_iteration_results(self, depth_image, color_image, color_frame, segmented_image):
        pass
    