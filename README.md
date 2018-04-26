
```sh
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo bash -C <<EOF
python3 get-pip.py
pip install --no-index --find-links=https://www.piwheels.org/simple opencv-python-armv7l
EOF
```