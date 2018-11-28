#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

#cp /usr/share/bluedonkey/images.html /run/bluedonkey/

if [ ! -e /sys/class/gpio/gpio69 ]; then
    echo 69 > /sys/class/gpio/export
fi

#case "$-" in
#    *i*)
#        echo "This shell is interactive"
#        ;;
#    *)
#        echo "This shell is not interactive"
#        ;;
#esac

echo "Starting BlueDonkey Python script"
python3 $(dirname $0)/line_follower.py
