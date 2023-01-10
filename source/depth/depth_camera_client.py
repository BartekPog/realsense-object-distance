
import os 

import numpy as np
import pyrealsense2 as rs


class DepthCameraClient:
    def __init__(self):     
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


    def get_aligned_images(self):
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
