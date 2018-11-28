#!/bin/sh
DIR=/opt/bluedonkey
systemctl stop bluedonkey.service
mkdir -p ${DIR}
install -m 644 bluedonkey.service ${DIR}
ln -sf ${DIR}/bluedonkey.service /etc/systemd/system/bluedonkey.service
install -m 744 bluedonkey_run.sh ${DIR}/
install -m 744 line_follower.py ${DIR}/
install -m 755 bluedonkey_listen.sh ${DIR}/
ln -sf ${DIR}/bluedonkey_listen.sh /usr/local/bin/bluedonkey_listen
systemctl enable bluedonkey.service
systemctl start bluedonkey.service

