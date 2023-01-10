import numpy as np
import pyrealsense2 as rs


from .processing_node import ProcessingNode

class ObjectCoordinatesDetector(ProcessingNode):
    target_topic = "object_coordinates"
    requires_segmentation = True

    def __init__(self):
        pass 
    
    def _get_object_coordinates(self, masked_depth, color_frame):
        intrinsics = color_frame.profile.as_video_stream_profile().intrinsics
        results = []
        width, height = masked_depth.shape
        
        for h in range(height):
            for w in range(width):
                if masked_depth[w,h]!=0:
                    results.append(rs.rs2_deproject_pixel_to_point(intrinsics, [w, h], masked_depth[w,h]))

        results = np.array(results).transpose()
        
        if results.size == 0:
            return (None, None, None)
            
        return (np.median(results[0] / 10),np.median(results[1] / 10),np.median(results[2] / 10)) # Milimeters

    def get_iteration_results(self, depth_image, color_image, color_frame, segmented_image):

        object_coordinates = []

        for index, class_name in enumerate(segmented_image['class_names']):
            mask = segmented_image['masks'][:, :, index]
            masked_depth = np.multiply(mask, depth_image)
            coordinates = self._get_object_coordinates(masked_depth=masked_depth, color_frame=color_frame)
            object_coordinates.append((class_name, coordinates))
        
        return object_coordinates
