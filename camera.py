#!/usr/bin/env python3
import os, sys
if not os.geteuid() == 0:
    sys.exit("\nPlease run as root.\n")
if sys.version_info < (3,0):
    sys.exit("\nPlease run under python3.\n")

import cv2
capture = cv2.VideoCapture(0)
capture.set(3, 160)
capture.set(4, 120)
ret, img = capture.read()
cv2.imwrite('capture.jpg',img)
capture.release()
