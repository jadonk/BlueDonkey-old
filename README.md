Switched to Buster now, so all this needs updating.

Some useful links:
* https://github.com/spmallick/learnopencv
* https://www.linkedin.com/learning/opencv-for-python-developers?trk=profileNonSelf_d_flagship3_profile_view_base_learningFeedm015%3Aa001_601786_learning
* https://gist.github.com/wroscoe/d7005216ab36cd4fa6ae0a5b428cbc1f#file-manage-py-L263
* http://docs.micropython.org/
* http://docs.openmv.io/library/omv.image.html
* https://github.com/openmv/openmv/blob/master/src/omv/img/stats.c
* https://openmv.io/blogs/news/linear-regression-line-following
* https://github.com/flatironinstitute/CaImAn/blob/master/caiman/base/rois.py
* https://github.com/jokla/CarND-LaneLines-P1/blob/master/P1.ipynb
* https://medium.com/@esmat.anis/robust-extrapolation-of-lines-in-video-using-linear-hough-transform-edd39d642ddf

The version of python-opencv for Debian Stretch is only for Python2 (https://packages.debian.org/stretch/python-opencv). You need to use Buster to get a build for Python3 (https://packages.debian.org/buster/python-opencv).

The pip repository for Python3 doesn't seem to have an armv7 build, so you need to use a version built for Raspberry Pi Zero or build it yourself.

The instructions below grab the Debian Stretch OpenCV library and the opencv-python pre-built for R-Pi0, assuming a Debian Stretch BeagleBone Blue image.

libjasper isn't in Debian Stretch, so it is built from source.

```sh
wget https://www.piwheels.org/simple/opencv-python/opencv_python-3.4.0.12-cp35-cp35m-linux_armv7l.whl#sha256=ff66665ddaa44d9a3a5271f4169ae865cdc3de897771dcc898053e8041fd2296
git clone https://github.com/mdadams/jasper
sudo bash -C <<EOF
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y cmake libjpeg62-turbo libtiff5 libpng16-16 libavcodec57 libavformat57 libswscale4 libv4l-0 libxvidcore4 libx264-148 libgtk2.0-bin libatlas3-base libwebp6 libopencv-dev libgstreamer1.0-0 libqtgui4 libqt4-test roboticscape python3 python3-pip python3-wheel xterm xauth libsdl1.2-dev
python3 -m wheel install opencv_python-3.4.0.12-cp35-cp35m-linux_armv7l.whl
#pip3 install rcpy
#pip3 install pygame
EOF
cd jasper
cmake . -DALLOW_IN_SOURCE_BUILD=1
make
sudo make install
sudo ln -s /usr/local/lib/libjasper.so.4 /usr/lib/libjasper.so.1
cd /opt/source/rcpy
git pull
sudo python3 setup.py install
```

# Update kernel and boot scripts

If you don't have a recent image, update some stuff first:

```sh
sudo bash -C <<EOF
cd /opt/scripts/tools
git pull
./update_kernel.sh --lts-4_14
cd developers
yes | ./update_bootloader.sh
EOF
```

Reboot

# Update distro

```sh
sudo bash -C <<EOF
apt-mark hold c9-core-installer
DEBIAN_FRONTEND=noninteractive apt-get -yq upgrade
EOF
```

# Buster

* https://rcn-ee.net/rootfs/bb.org/testing/2018-06-04/buster-iot/bone-debian-buster-iot-armhf-2018-06-04-4gb.img.xz

```sh
sudo apt-get update
sudo apt-get install -y python3-pip python3-wheel python3-opencv libopencv-dev
```