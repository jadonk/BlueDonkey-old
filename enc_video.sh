#!/bin/sh
name=bluedonkey-run-`date +%Y%m%d%H%M%S`
#cd /var/lib/cloud9/mnt
cd /run/bluedonkey
ffmpeg -r 5 -i res%05d.png ${name}.mp4
#ffmpeg -r 5 -i cam%05d.png ${name}-cam.mp4
#ffmpeg -r 5 -i res%05d.png ${name}-res.mp4
#ffmpeg -filter_complex hstack -i ${name}-cam.mp4 -i ${name}-res.mp4 ${name}.mp4
cp ${name}.mp4 /run/bluedonkey/bluedonkey-run-latest.mp4

mkdir -p /var/lib/cloud9/mnt/${name}
mv *.png /var/lib/cloud9/mnt/${name}/
mv ${name}.mp4 /var/lib/cloud9/mnt/
