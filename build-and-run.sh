docker build -f Dockerfile --network=host -t realsense-build-depth -t realsense-build-depth:latest . 
sudo docker run --privileged -it --rm realsense-build-depth
