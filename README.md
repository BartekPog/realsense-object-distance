# ROS realsense object detection in 3D space
Depth perception cameras are a necessary asset for building interactive mobile robots. Interactivity requires reliable environment perception and understanding - this is why we developed a tool for detecting surrounding objects and measuring distance and relative position. 


### Tech stack
- Intel Realsense camera
- Robot Operating System (ROS)
- rosbridge
- Docker
- python
  - numpy
  - pixellib
  - roslibpy


# How to use
### Prerequisites
1. You have a device running [ROS](https://www.ros.org/)
1. [rosbridge_server](http://wiki.ros.org/rosbridge_server) package is installed
1. [Docker](https://www.docker.com/) is installed
1. You have a [realsense](https://www.intelrealsense.com/) camera


## Installation
Clone this repository to the device which runs ROS and has the realsense cameras connected
```bash
git clone git@github.com:IntelRealSense/librealsense.git
```
Download the segmentation model using the `source/segmentation/models/get_model.sh` script
```bash
cd source/segmentation/models/
chmod +x get_model.sh
./get_model.sh
```

Launch `rosbridge_server` on port 9090 (default)

```bash
roslaunch rosbridge_server rosbridge_websocket.launch 
```

Update the configuration if needed - Update the `source/processing_pipeline.py` file to do so - you may want to set the `segmentation_image_path` to `None` after you are done debugging your project to avoid the growing disk usage. 

After you are done tweaking the code, run:
```bash
chmod +x build-and-run.sh
./build-and-run.sh
```
The initial build takes about 10-20 minutes, as the `librealsense` needs to be compiled. If the build was successful, you will be prompted for your sudo password (as the container needs to access camera). 

If the camera is available and ROS works properly, you should start seeing readings on the ROS topics. For example: 
```
data: "[[\"person\", 181.3062226450999]]"
data: "[[\"person\", 171.36484450923226], [\"cell phone\", 255.94315971471797]]"
```

we use milimeters as our default unit. 



## Implementing your own image processing node
To build your own processing node, simply implement a new `processing_nodes.ProcessingNode` child class and import it in the `processing_nodes.__init__.py` file. That's all! IT will be automatically added to the processing pipeline. You can take the [ObjectDistanceDetector](https://github.com/BartekPog/realsense-object-distance/blob/main/source/processing_nodes/object_distance_detector.py) class as a starting point.


### Why Docker?
Installing [Intel Realsense drivers](https://github.com/IntelRealSense/librealsense) might be annoying in some cases, thus we contained the whole pipeline within a Docker container. It please note that docker container is not used here for security reasons - the container still needs to be run with privileged account, on host network - thus we do not provide a ready-made docker image. In our experiments we used turtlebot2i, running ubuntu 16.10, which was utilized for other projects as well. To have freedom of non-legacy tech stack without the risk of breaking some configurations for other students we decided to keep all our work within a container


## Further work
This project might be a part of a larger interactive platform. It still needs to be highly adjusted for that though. 
1. Currently all the detected objects information is being sent to ROS topics as JSON encoded dictionaries. It is not an optimal solution, as it requires string parsing on the receiving node. Please feel free to submit a pull request if you come up with a 'cleaner' way of handling that.
1. Currently there is no direct external configuration file for eg. changing the destination topics, rosbridge port or toggling whether to store the segmentation images or not. Having a single `yaml` or `json` file might speed up the process of interacting with this package. 
1. On Turtlebot2i segmentation takes about 3 seconds for each image, as entire inference is processed on CPU (as NUC on turtlebot does not have any GPU). The code will probably need some adjustments to utilize any GPU onboard. 
1. In case you decide to use more that one Realsense camera in your robot, you most probably will need to update the code to specify which camera should the script use. 

