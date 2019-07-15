# Example from https://github.com/jacksonliam/mjpg-streamer/blob/master/mjpg-streamer-experimental/plugins/input_opencv/filters/cvfilter_py/example_filter.py
import cv2
import numpy

COLOR_THRESHOLD_MIN = 250
COLOR_THRESHOLD_MAX = 254
COLOR_THRESHOLD_DELTA = 1
PERCENT_THRESHOLD_MIN = 2
PERCENT_THRESHOLD_MAX = 20
FRAME_WIDTH = 160
FRAME_HEIGHT = 120
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Array of region of interest masks in the order they should be searched
# Furthest away first
roi_masks = numpy.array([
        # Focus on the center
        # 8/20ths in from the left
        # 8/20ths down from the top
        # 1/20ths tall
        # 4x1 pixel count
        [int(8*FRAME_WIDTH/20), int(8*FRAME_HEIGHT/20), int(1*FRAME_HEIGHT/20), int((4*FRAME_WIDTH/20)*(1*FRAME_HEIGHT/20)/100)],
        # Then look wider
        # 6/20ths in from the sides
        # 9/20ths down from the top
        # 1/20ths tall
        # 8x1 pixel count
        [int(6*FRAME_WIDTH/20), int(9*FRAME_HEIGHT/20), int(1*FRAME_HEIGHT/20), int((8*FRAME_WIDTH/20)*(1*FRAME_HEIGHT/20)/100)],
        # Then look wider
        # 4/20ths in from the sides
        # 10/20ths down from the top
        # 1/20ths tall
        # 12x1 pixel count
        [int(4*FRAME_WIDTH/20), int(10*FRAME_HEIGHT/20), int(1*FRAME_HEIGHT/20), int((12*FRAME_WIDTH/20)*(1*FRAME_HEIGHT/20)/100)],
        # Then really wide and taller
        # 0/20ths in from the sides
        # 11/20ths down from the top
        # 1/20ths tall
        # 20x1 pixel count
        [int(0*FRAME_WIDTH/10), int(11*FRAME_HEIGHT/20), int(1*FRAME_HEIGHT/20), int((20*FRAME_WIDTH/20)*(1*FRAME_HEIGHT/20)/100)],
    ], dtype=numpy.int32)

frame_cnt = 0
threshold = COLOR_THRESHOLD_MAX

class MyFilter:
    def process(self, img):
        global frame_cnt, threshold

        # Image comes in at 640x480, so turn it into 160x120
        frame = img[::4,::4].copy()
        
        try:
            line = False
            pixel_cnt = 0
            pixel_cnt_min = int(PERCENT_THRESHOLD_MIN*roi_masks[2][3])
            pixel_cnt_max = int(PERCENT_THRESHOLD_MAX*roi_masks[2][3])
            for roi_mask in roi_masks:
                # roi_mask[0] pixels in from the sides
                # roi_mask[1] pixels down from the top
                # roi_mask[2] pixels high
                # roi_mask[3] number of pixels / 100
                if (not line) or (pixel_cnt < pixel_cnt_min):
                    # Extract blue only in ROI
                    top = roi_mask[1]
                    bottom = roi_mask[1] + roi_mask[2] - 1
                    left = roi_mask[0]
                    right = FRAME_WIDTH-roi_mask[0]-1
                    blue = frame[ top : bottom , left : right , 0 ]
                    # Zero out pixels below threshold
                    thresh_mask = cv2.inRange(blue, threshold, 255)
                    # Get array of pixel locations that are non-zero
                    pixelpoints = cv2.findNonZero(thresh_mask)
                    if pixelpoints is not None:
                        pixel_cnt = pixelpoints.size
                        pixel_cnt_min = int(PERCENT_THRESHOLD_MIN*roi_mask[3])
                        pixel_cnt_max = int(PERCENT_THRESHOLD_MAX*roi_mask[3])
                        vx = 0
                        vy = 1
                        y = int((top+bottom) / 2)
                        x = int(pixelpoints[:,:,0].mean()) + roi_mask[0]
                        line = [vx,vy,x,y]
                        thresh_color = cv2.cvtColor(thresh_mask, cv2.COLOR_GRAY2BGR)
                        frame[ top : bottom , left : right ] = thresh_color

            status = "test"
            #cv2.putText(frame, status, (10,FRAME_HEIGHT-(int(FRAME_HEIGHT/4))), FONT, 0.3, (150,150,255))
            if line:
                frame = cv2.line(frame, (x,0), (x,y), (0,255,0), 2)

            # Adjust threshold if finding too few or too many pixels
            if pixel_cnt > pixel_cnt_max:
                threshold += COLOR_THRESHOLD_DELTA
                if threshold > COLOR_THRESHOLD_MAX:
                    threshold = COLOR_THRESHOLD_MAX
            if pixel_cnt < pixel_cnt_min:
                threshold -= COLOR_THRESHOLD_DELTA
                if threshold < COLOR_THRESHOLD_MIN:
                    threshold = COLOR_THRESHOLD_MIN

        except Exception as e: print(e)

        return frame
        
def init_filter():
    f = MyFilter()
    return f.process
