#
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html

import cv2
import numpy as np
import glob
import time
import re
from scipy.signal import savgol_filter
from detect_peaks import detect_peaks
from BirdsEyeTransform import BirdsEyeTransform
from PID import PID

"""
PARAMETERS
"""

g_PAUSED = True   # Initial Paused state

# Image/Camera settings
FRAME_EXPOSURE = 0
FRAME_WIDTH = 160
FRAME_HEIGHT = 120
CAM_FPS = 30

# Image Retrieval
READ_FROM_DIR = True
#DATA_DIR = "data/tub_8_18-03-31/"
#PREFIX = ""
#DATA_DIR = "data/data_20180724_01/"
DATA_DIR = "data/data_20180724_02/"
PREFIX = "cam"

# Masking
ROI_VERTICES = np.array([[0,FRAME_HEIGHT-1], [0,90], # Left side
                         [40,20], [FRAME_WIDTH-41,20], # Top
                         [FRAME_WIDTH-1,90], [FRAME_WIDTH-1,FRAME_HEIGHT-1] # Right side
                        ], dtype=np.int32)

'''
# Original
ROI_VERTICES = np.array([[0,119], [0,90], [70,20], [90,20], [159,90], [159,119]], dtype=np.int32)
'''

# Raspi Wide angle
'''
ROI_VERTICES = np.array([[0,119], [0,90], # Left side
                         [50,60], [110,60], # Top
                         [159,90], [159,119] # Right side
                        ], dtype=np.int32)
'''

"""
UTILITY FUNCTIONS
"""

def getFileNum(pathname):
    m = re.search("[^0-9]*(\d+)[^0-9]*\.(png|jpg)$", pathname)
    return int(m.group(1))

def getPausedState():
    global g_PAUSED
    if g_PAUSED:
        return "PAUSED"
    else:
        return "UNPAUSED"

def createDirFrameGenerator(sorted_img_filenames):
    # Read the images in numeric order
    for filename in sorted_img_filenames:
        yield cv2.imread(filename)

def onBrightLowerUpdate(userdata):
    global g_brightLowerThresh
    g_brightLowerThresh = userdata

def onBrightUpperUpdate(userdata):
    global g_brightUpperThresh
    if (userdata < g_brightLowerThresh):
        cv2.setTrackbarPos('BrightUpper', 'combined', g_brightLowerThresh + 1)
        g_brightUpperThresh = g_brightLowerThresh + 1
    else:
        g_brightUpperThresh = userdata

def onFPSUpdate(userdata):
    global g_displayFPS
    if userdata == 0:
        g_displayFPS = 1
        cv2.setTrackbarPos('FPS', 'combined', 1)
    else:
        g_displayFPS = userdata

def onFrameUpdate(userdata):
    global g_frameCount
    g_frameCount = userdata

def fitLineToPixels(img):
    pixelpoints = cv2.findNonZero(img)
    if pixelpoints is not None:
        try:
            # [vx, vy, x, y]
            line = cv2.fitLine(pixelpoints, cv2.DIST_L2, 0, 0.01, 0.01)
            #print ("found line: {}".format(line))
        except:
            line = None
    else:
        line = None

    return line

def fitLineToXAvg(gray):
    pixelpoints = cv2.findNonZero(gray)
    if pixelpoints is not None:
        vx = 0.001
        vy = 1.
        x = float(pixelpoints[:,:,0].mean())
        y = 50.
        #line = np.array([[vx],[vy],[x],[y]])
        line = [vx,vy,x,y]
    else:
        line = None

    return line

def drawLineOnImg(line, img):
    if line is not None:
        [vx, vy, x, y] = line
        try:
            lefty = int((-x*vy/vx) + y)
            righty = int(((img.shape[1]-x)*vy/vx)+y)
            img = cv2.line(img, (img.shape[1]-1,righty), (0,lefty), (0,255,0), 2)
        except:
            pass
    return img

def drawMeterOnImg(line, img):
    if line is not None:
        [vx, vy, x, y] = line
        try:
            img = cv2.line(img, (img.shape[1]//2, int(y)+10), (img.shape[1]//2, int(y)-10), (0,0,255), 2) # center reference
            img = cv2.line(img, (int(x), int(y+5)), (int(x), int(y)-5), (0,255,0), 2) # average
        except:
            pass

    return img

def softmax(x):
    '''Compute softmax values for each value in x.'''
    return np.exp(x) / np.sum(np.exp(x), axis=0)

def g2c(img):
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def c2v(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return hsv[:,:,2]

def find_threshold(gray, show_plot=False):

    hist, bin_edges = np.histogram(gray, 255)
    padded = np.append(hist, [1, 0, 0])

    smoothed = savgol_filter(padded, 9, 3)
    peaks = detect_peaks(smoothed, mpd=5, threshold=0.25, show=show_plot)

    right_idx = peaks[-1]
    left_max = -1
    left_idx = -1
    for p in peaks[:-1]:
        if smoothed[p] > left_max:
            left_max = smoothed[p]
            left_idx = p

    #print ("left_idx: {} right_idx: {}".format(left_idx, right_idx))

    if left_idx == -1:
        left_idx = 191 # put at 75%
        #print ("left_idx not detected. setting to {}".format(left_idx))

    minimums = detect_peaks(smoothed[left_idx:right_idx], mpd=21, valley=True, edge='falling', show=show_plot)

    min_val = 300 # more than 255 max value
    min_idx = -1
    for p in minimums:
        if smoothed[left_idx + p] < min_val:
            min_val = smoothed[left_idx + p]
            min_idx = p

    #print ("min_idx: {} (adjusted: {}), min_val: {}".format(min_idx, min_idx + left_idx, min_val))

    return int(left_idx + min_idx)

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / N

def get_next_thresh(thresh):
    global g_thresholds
    g_thresholds = np.delete(g_thresholds, 0)
    g_thresholds = np.append(g_thresholds, thresh)
    mean = np.mean(g_thresholds)
    # print ("mean {}".format(mean))
    return int(mean)

def get_thresholded_img(img):
    global g_brightLowerThresh, g_brightUpperThresh, ROI_MASK, ROI_VERTICES, g_slidersCreated

    # Convert BGR to HSV and extract the brightness value
    bright = c2v(img)

    # Filter based on threshold values
    thresh = find_threshold(bright) # get the instantaneous threshold reading

    if g_PAUSED == False:
        g_brightLowerThresh = get_next_thresh(thresh)
    else:
        pass

    if (g_slidersCreated == True):
        cv2.setTrackbarPos('BrightLower', 'combined', g_brightLowerThresh)

    threshold_mask = cv2.inRange(bright, g_brightLowerThresh, g_brightUpperThresh)
    return [bright, threshold_mask]

def mask_and_draw_lines(gray, threshold_mask, apply_roi=True):
    masked = cv2.bitwise_and(gray, gray, mask=threshold_mask)

    # Filter out ROI
    if apply_roi == True:
        masked = cv2.bitwise_and(masked, masked, mask=ROI_MASK)

    masked_color = g2c(masked)

    # Draw our detected line and ROI on the img
    #line = fitLineToPixels(masked)
    #res_color = drawLineOnImg(line, masked_color)

    line = fitLineToXAvg(masked)
    res_color = drawMeterOnImg(line, masked_color)

    if apply_roi == True:
        res_color = cv2.polylines(res_color, [ROI_VERTICES], 1, (255, 0, 0))

    return res_color

"""
SET UP
"""

g_slidersCreated = False

g_thresholds = np.zeros(5, dtype=np.uint8)

# Adjustment values
BRIGHT_LOWER_DEFAULT = 180
BRIGHT_UPPER_DEFAULT = 255
g_brightLowerThresh = BRIGHT_LOWER_DEFAULT
g_brightUpperThresh = BRIGHT_UPPER_DEFAULT

DISPLAY_FPS_MAX = 30
DISPLAY_FPS_DEFAULT = 10
g_displayFPS = DISPLAY_FPS_DEFAULT

# Masking
ROI_MASK = np.zeros((FRAME_HEIGHT, FRAME_WIDTH), np.uint8)
cv2.fillConvexPoly(ROI_MASK, ROI_VERTICES, 255)

# Camera Set-up
frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
if (READ_FROM_DIR == False):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, CAM_FPS)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if FRAME_EXPOSURE > 0:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        cap.set(cv2.CAP_PROP_EXPOSURE, FRAME_EXPOSURE)
else:
    img_filenames = glob.glob(DATA_DIR + PREFIX + "*.png") + glob.glob(DATA_DIR + PREFIX + "*.jpg")
    sorted_img_filenames = sorted(img_filenames, key=getFileNum)
    #fileFrameGen = createDirFrameGenerator(sorted_img_filenames)
    g_frameCount = 0
    g_frameTotal = len(sorted_img_filenames)


# Set up the birds eye transformation
t_y = int(0.2 * FRAME_HEIGHT)
b_y = int(1.0 * FRAME_HEIGHT)
tl_x = int(0.25 * FRAME_WIDTH)
tr_x = int(0.75 * FRAME_WIDTH)
bl_x = int(0.0 * FRAME_WIDTH)
br_x = int(1.0 * FRAME_WIDTH)

d_t_y = int(FRAME_HEIGHT * 0.2)
d_b_y = int(FRAME_HEIGHT - 1)
d_l_x = int(0.18 * FRAME_WIDTH)
d_r_x = int(0.82 * FRAME_WIDTH)

#                          TL             TR             BR             BL
trans_src = np.float32([(tl_x,t_y),    (tr_x,t_y),    (br_x,b_y),    (bl_x,b_y)])
trans_dst = np.float32([(d_l_x,d_t_y), (d_r_x,d_t_y), (d_r_x,d_b_y), (d_l_x,d_b_y)])

bird = BirdsEyeTransform(w=FRAME_WIDTH, h=FRAME_HEIGHT, src=trans_src, dst=trans_dst)

"""
MAIN LOOP
"""

while(1):

    # Take each frame
    if not g_PAUSED:
        if (READ_FROM_DIR == False):
            _, frame = cap.read()
        else:
            now = time.time()
            try:
                #frame = next(fileFrameGen)
                frame = cv2.imread(sorted_img_filenames[g_frameCount])
                if g_frameCount < g_frameTotal - 1:
                    g_frameCount += 1
                else:
                    g_frameCount = g_frameTotal - 1
            except StopIteration:
                pass
    else:
        if (READ_FROM_DIR == True):
            now = time.time()
            frame = cv2.imread(sorted_img_filenames[g_frameCount])

    #print ("frame shape: {}".format(frame.shape))

    # Process frame
    [bright, threshold_mask] = get_thresholded_img(frame)
    res_color = mask_and_draw_lines(bright, threshold_mask)
    # Prep pipeline images for display
    row1 = np.hstack([frame, g2c(bright), g2c(threshold_mask), res_color])

    # Now do the same for the birdseye
    bird_warp = bird.warp(frame)
    [bird_bright, bird_threshold_mask] = get_thresholded_img(bird_warp)
    bird_res_color = mask_and_draw_lines(bird_bright, bird_threshold_mask, apply_roi=True)

    bird_before_src = np.copy(frame)
    bird.draw_src_on_img(bird_before_src)

    bird_bright_dst = np.copy(g2c(bird_bright))
    bird.draw_dst_on_img(bird_bright_dst)

    # Prep pipeline images for display
    row2 = np.hstack([bird_before_src, bird_bright_dst, g2c(bird_threshold_mask), bird_res_color])

    combined = np.vstack([row1, row2])

    cv2.imshow('combined', combined)
    if (g_slidersCreated == False):
        if (READ_FROM_DIR == True):
            cv2.createTrackbar('FPS', 'combined', g_displayFPS, DISPLAY_FPS_MAX, onFPSUpdate)
            cv2.createTrackbar('Frame', 'combined', g_frameCount, g_frameTotal-1, onFrameUpdate)
        cv2.createTrackbar('BrightLower', 'combined', g_brightLowerThresh, 255, onBrightLowerUpdate)
        cv2.createTrackbar('BrightUpper', 'combined', g_brightUpperThresh, 255, onBrightUpperUpdate)
        g_slidersCreated = True

    if (READ_FROM_DIR == True and g_slidersCreated == True):
        cv2.setTrackbarPos('Frame', 'combined', g_frameCount)

    # Read images at intended rate
    if (READ_FROM_DIR == True):
        elapsed = time.time() - now
        diff = (1./g_displayFPS) - elapsed
        if (diff > 0):
            time.sleep(diff)

    # Look for cancel signal (control-c)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
    elif k == 32:
        g_PAUSED = not g_PAUSED
        if (READ_FROM_DIR == True):
            print ("Space pressed. Paused? {}, Frame: {}".format(g_PAUSED, g_frameCount))
        else:
            print ("Space pressed. Paused? {}".format(g_PAUSED))

cv2.destroyAllWindows()
