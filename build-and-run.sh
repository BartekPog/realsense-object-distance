docker build -f Dockerfile-newest --network=host -t realsense-build-depth -t realsense-build-depth:latest . 
sudo docker run --privileged -it --rm realsense-build-depth