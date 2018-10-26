#!/bin/sh
#/usr/bin/mjpg_streamer -i "/usr/lib/mjpg-streamer/input_file.so -e -f ${PWD}" -o "/usr/lib/mjpg-streamer/output_http.so -p 8090 -w /usr/share/mjpg-streamer/www"
mkdir -p /run/bluedonkey
chown debian.debian /run/bluedonkey
chmod ugo+rwx /run/bluedonkey
cp images.html /run/bluedonkey/
echo 69 > /sys/class/gpio/export
mkfifo /run/bluedonkey/pipe
python3 line_follower.py
