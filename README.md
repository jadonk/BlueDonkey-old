Latest version is at https://github.com/jadonk/BlueDonkey

# Setup image

This is based on Debian Buster, which has support for python3-opencv.

* Program the following image using Etcher.io:
  * https://debian.beagleboard.org/images/bone-debian-buster-iot-armhf-2018-06-17-4gb.img.xz
* Add python3-pygame from sid.  See https://www.debian.org/doc/manuals/apt-howto/ch-apt-get.en.html#s-default-version
* Install other needed python3 packages
```sh
sudo apt-get update
sudo apt-get install -y python3-pip python3-wheel python3-opencv libopencv-dev
```

# Build car

* https://github.com/Sashulik/Detroit-Autonomous-Vehicle-Group/tree/master/BeagleBone-Blue_DonkeyCar

# Run

Set BINARY_VIEW if you want to save images. You'll also need to nsert a microSD card and mount it at IMG_DIR.

```sh
sudo ./line_follower.py
```

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



