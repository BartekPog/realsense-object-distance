# Installs librealsense and pyrealsense2 on the Jetson NX running Ubuntu 18.04
# and using Python 3
# Tested on a Jetson NX running Ubuntu 18.04 and Python 3.6.9 on 2020-11-04

FROM python:3.9-bullseye as librealsense

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y --no-install-recommends \
    python3 \
    python3-setuptools \
    python3-pip \
    python3-dev\
    cmake

# Install the core packages required to build librealsense libs
RUN apt-get install -y git libssl-dev libusb-1.0-0-dev pkg-config libgtk-3-dev
# Install Distribution-specific packages for Ubuntu 18
RUN apt-get install -y libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev

# Install LibRealSense from source
# We need to build from source because
# the PyPi pip packages are not compatible with Arm processors.
# See link [here](https://github.com/IntelRealSense/librealsense/issues/6964).

# First clone the repository

RUN mkdir -p /realsense

WORKDIR /realsense
RUN git clone https://github.com/IntelRealSense/librealsense.git
WORKDIR /realsense/librealsense

# Make sure that your RealSense cameras are disconnected at this point
# Run the Intel Realsense permissions script
RUN bash ./scripts/setup_udev_rules.sh

RUN mkdir -p /realsense/librealsense/build
WORKDIR /realsense/librealsense/build

## Install CMake with Python bindings (that's what the -DBUILD flag is for)
## see link: https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python#building-from-source
RUN cmake ../ -DBUILD_PYTHON_BINDINGS:bool=true
## Recompile and install librealsense binaries
## This is gonna take a while! The -j4 flag means to use 4 cores in parallel
## but you can remove it and simply run `sudo make` instead, which will take longer # make uninstall && sudo make clean && 
RUN make -j4 && make install

## Export pyrealsense2 to your PYTHONPATH so `import pyrealsense2` works
ENV PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.9/site-packages/pyrealsense2



COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY ./source ./source

CMD ["uvicorn", "source.server:app", "--host", "0.0.0.0", "--port", "80"]
