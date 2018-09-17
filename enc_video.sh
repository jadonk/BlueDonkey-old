#!/bin/sh
name=bluedonkey-run-`date +%Y%m%d%S`
cd /var/lib/cloud9/mnt
ffmpeg -r 2 -filter_complex hstack -i cam%05d.png -i res%05d.png ${name}.mp4
mkdir ${name}
mv *.png ${name}/
