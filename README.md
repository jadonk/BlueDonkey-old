Latest version is at https://github.com/jadonk/BlueDonkey

# Setup image

This is based on Debian Buster, which has support for python3-opencv.

* Program the following image using Etcher.io:
  * ~~https://rcn-ee.net/rootfs/bb.org/testing/2018-12-16/buster-iot/bone-debian-buster-iot-armhf-2018-12-16-4gb.img.xz~~
  * https://rcn-ee.net/rootfs/bb.org/testing/2019-03-24/buster-iot/bone-debian-buster-iot-armhf-2019-03-24-4gb.img.xz

* Get your board on the Internet
  * Your board should have an SSID of BeagleBone-XXXX, where XXXX is random. Password is 'BeagleBone'.
  * Connect to http://192.168.8.1 via your web browser to get to the console/IDE.
  * Run 'sudo connmanctl' at the console to connect to the Internet using your own access point.
```
scan wifi
services
agent on
connect <<your access point ID>>
quit
```

* Install BlueDonkey and dependencies
```sh
sudo apt-get update
sudo apt-get install -y python3-pip python3-wheel python3-opencv libopencv-dev python3-pygame
git clone https://github.com/jadonk/bluedonkey
cd bluedonkey
sudo ./install.sh
```

# Build car

* https://github.com/Sashulik/Detroit-Autonomous-Vehicle-Group/tree/master/BeagleBone-Blue_DonkeyCar

# Run

Set BINARY_VIEW if you want to save images. You'll also need to nsert a microSD card and mount it at IMG_DIR.

The RED LED should come up on boot.

You should be able to monitor the running line follower application.
```sh
bluedonkey_listen
```

Press the PAU (pause) button to start driving! The RED LED should go off and the GREEN LED should turn on.

# Other

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



