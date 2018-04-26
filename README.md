
```sh
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
wget https://www.piwheels.org/simple/opencv-python/opencv_python-3.4.0.12-cp35-cp35m-linux_armv7l.whl#sha256=ff66665ddaa44d9a3a5271f4169ae865cdc3de897771dcc898053e8041fd2296
sudo bash -C <<EOF
python3 get-pip.py
wheel install opencv_python-3.4.0.12-cp35-cp35m-linux_armv7l.whl
EOF
```