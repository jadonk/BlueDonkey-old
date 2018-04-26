The version of python-opencv for Debian Stretch is only for Python2 (https://packages.debian.org/stretch/python-opencv). You need to use Buster to get a build for Python3 (https://packages.debian.org/buster/python-opencv).

The pip repository for Python3 doesn't seem to have an armv7 build, so you need to use a version built for Raspberry Pi Zero or build it yourself.

The instructions below grab the Debian Stretch OpenCV library and the opencv-python pre-built for R-Pi0, assuming a Debian Stretch BeagleBone Blue image.

```sh
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
wget https://www.piwheels.org/simple/opencv-python/opencv_python-3.4.0.12-cp35-cp35m-linux_armv7l.whl#sha256=ff66665ddaa44d9a3a5271f4169ae865cdc3de897771dcc898053e8041fd2296
sudo bash -C <<EOF
apt-get update
apt-get install -y libatlas3-base libwebp6 libopencv-dev
python3 get-pip.py
wheel install opencv_python-3.4.0.12-cp35-cp35m-linux_armv7l.whl
EOF
```