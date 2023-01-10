mkdir segmentation-images || echo "segmentation-images directory already exists"

docker build -f Dockerfile --network=host -t realsense-build-depth -t realsense-build-depth:latest . 
sudo docker run \
    --network=host \
    --privileged \
    -it \
    --rm \
    -v $(pwd)/segmentation-images:/realsense/librealsense/build/segmentation-images \
    realsense-build-depth
