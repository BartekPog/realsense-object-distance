import numpy as np

from .processing_node import ProcessingNode

class ObjectCoordinatesDetector(ProcessingNode):
    target_topic = "object_coordinates"
    requires_segmentation = True

    def __init__(self):
        pass 
    
    def _get_object_coordinates(self, masked_depth, color_frame):
        intrinsics = color_frame.profile.as_video_stream_profile().intrinsics
        results = []
        height, width = masked_depth.shape
        
        for x in range(height):
            for y in range(width):
                if masked_depth[x,y]!=0:
                    results.append(rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], masked_depth[x,y]))
        
        results = np.array(results).transpose()
        
        if results.size == 0:
            return (None, None, None)
            
        return (np.mean(results[0]), np.mean(results[1]), np.mean(results[2]))
        
    def get_iteration_results(self, depth_image, color_image, color_frame, segmented_image):

        object_coordinates = []

        for index, class_name in enumerate(segmented_image['class_names']):
            mask = segmented_image['masks'][:, :, index]
            masked_depth = np.multiply(mask, depth_image)
            coordinates = self._get_object_coordinates(masked_depth=masked_depth, color_frame=color_frame)
            object_coordinates.append((class_name, coordinates))
        
        return object_coordinates
