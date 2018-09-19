#!/bin/sh
if [ -z "$1" ]; then
    name=bluedonkey-run-`date +%Y%m%d%H%M%S`
else
    name=$1
fi
mkdir -p /var/lib/cloud9/mnt/${name}
mv /run/bluedonkey/*.png /var/lib/cloud9/mnt/${name}/
mv /var/lib/cloud9/mnt/*.png /var/lib/cloud9/mnt/${name}/
cd /var/lib/cloud9/mnt/${name}
ffmpeg -r 10 -i res%05d.png ${name}.mp4
#ffmpeg -r 5 -i cam%05d.png ${name}-cam.mp4
#ffmpeg -r 5 -i res%05d.png ${name}-res.mp4
#ffmpeg -filter_complex hstack -i ${name}-cam.mp4 -i ${name}-res.mp4 ${name}.mp4
cp ${name}.mp4 /run/bluedonkey/bluedonkey-run-latest.mp4
