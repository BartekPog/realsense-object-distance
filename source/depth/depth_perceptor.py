
import os 

import numpy as np
import pyrealsense2 as rs

from pixellib.torchbackend.instance import instanceSegmentation



class DepthPerceptor:
    def __init__(self):
        # Init segmentation model
        self.model = instanceSegmentation()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(dir_path, "models/pointrend_resnet50.pkl")
        self.model.load_model(model_path)
        
        # Init image pipeline
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = self.config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        align_to = rs.stream.color
        self.align = rs.align(align_to)

        found_rgb = False
        for s in device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break

        if not found_rgb:
            raise Exception(f"{str(self.__class__)}requires Depth camera with Color sensor")

        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        if device_product_line == 'L500':
            self.config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
        else:
            self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        self.pipeline_started = False


    def _start_streaming_pipeline(self):
        if self.pipeline_started:
            print("Pipeline already started")
            return

        self.pipeline.start(self.config)
        self.pipeline_started = True

    def _stop_streaming_pipeline(self):
        if not self.pipeline_started:
            print("Pipeline already stopped")
            return

        self.pipeline.stop()
        self.pipeline_started = False


    def __del__(self):
        self._stop_streaming_pipeline()

    def _get_aligned_images(self):
        if not self.pipeline_started:
            self._start_streaming_pipeline()

        # Get frameset of color and depth
        frames = self.pipeline.wait_for_frames()
        
        # Align the depth frame to color frame
        aligned_frames = self.align.process(frames)
        
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            raise('Invalid camera config')

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        return depth_image, color_image,color_frame

    def segment_image(self, image):
        segmentation, _ = self.model.segmentFrame(image)

        return segmentation

    def get_object_coordinates(self, masked_depth, color_frame):
        intrinsics = color_frame.profile.as_video_stream_profile().intrinsics
        results = []
        width, height  = masked_depth.shape
        
        for h in range(height):
            for w in range(width):
                if masked_depth[w,h]!=0:
                    results.append(rs.rs2_deproject_pixel_to_point(intrinsics, [w, h], masked_depth[w,h]))
        
        results = np.array(results).transpose()
        
        if results.size == 0:
            return (None, None, None)
            
        return (np.median(results[0]),np.median(results[1]),np.median(results[2]))

    def get_depth(self):
        depth_image, color_image, _  = self._get_aligned_images()

        segmentation = self.segment_image(color_image)

        object_distances = []

        for index, class_name in enumerate(segmentation['class_names']):
            mask = segmentation['masks'][:, :, index]
            masked_depth = np.multiply(mask, depth_image)
            average_depth = np.sum(masked_depth) / np.count_nonzero(masked_depth)
            object_distances.append((class_name, average_depth))

        return object_distances

    def get_coordinates(self):
        depth_image, color_image, color_frame = self._get_aligned_images()

        segmentation = self.segment_image(color_image)

        object_coordinates = []

        for index, class_name in enumerate(segmentation['class_names']):
            mask = segmentation['masks'][:, :, index]
            masked_depth = np.multiply(mask, depth_image)
            coordinates = self.get_object_coordinates(masked_depth=masked_depth, color_frame=color_frame)
            object_coordinates.append((class_name, coordinates))
        
        return object_coordinates
        


if __name__ == "__main__":
    dp = DepthPerceptor()
    dp.get_depth()
