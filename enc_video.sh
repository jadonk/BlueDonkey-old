#!/bin/sh
name=bluedonkey-run-`date +%Y%m%d%H%M%S`
cd /var/lib/cloud9/mnt
ffmpeg -r 5 -i cam%05d.png ${name}-cam.mp4
ffmpeg -r 5 -i res%05d.png ${name}-res.mp4
ffmpeg -filter_complex hstack -i ${name}-cam.mp4 -i ${name}-res.mp4 ${name}.mp4
mkdir ${name}
mv *.png ${name}/
