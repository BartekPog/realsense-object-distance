import numpy as np 

from .processing_node import ProcessingNode


class ObjectDistanceDetector(ProcessingNode):
    target_topic = "object_distances"
    requires_segmentation = True

    def get_iteration_results(self, depth_image, color_image, color_frame, segmented_image):
        object_distances = []

        for index, class_name in enumerate(segmented_image['class_names']):
            mask = segmented_image['masks'][:, :, index]
            masked_depth = np.multiply(mask, depth_image)
            average_depth = np.sum(masked_depth) / np.count_nonzero(masked_depth) * 10 # Milimeters
            object_distances.append((class_name, average_depth))

        return object_distances
