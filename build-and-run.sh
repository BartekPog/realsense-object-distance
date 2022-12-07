docker build -f Dockerfile --network=host -t realsense-build-depth -t realsense-build-depth:latest . 
sudo docker run --privileged -it -p 8082:80 --rm realsense-build-depth
