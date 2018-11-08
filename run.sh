#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

#/usr/bin/mjpg_streamer -i "/usr/lib/mjpg-streamer/input_file.so -e -f ${PWD}" -o "/usr/lib/mjpg-streamer/output_http.so -p 8090 -w /usr/share/mjpg-streamer/www"
if [ ! -e /run/bluedonkey ]; then
    mkdir -p /run/bluedonkey
    chown debian.debian /run/bluedonkey
    chmod ugo+rwx /run/bluedonkey
fi

#cp /usr/share/bluedonkey/images.html /run/bluedonkey/

if [ ! -e /sys/class/gpio/gpio69 ]; then
    echo 69 > /sys/class/gpio/export
fi

if [ ! -e /run/bluedonkey/pipeout ]; then
    mkfifo /run/bluedonkey/pipeout
fi
if [ ! -e /run/bluedonkey/pipein ]; then
    mkfifo /run/bluedonkey/pipein
fi

echo "Starting BlueDonkey Python script"
python3 line_follower.py
