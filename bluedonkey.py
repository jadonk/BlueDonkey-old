#!/usr/bin/env python3
import os, sys, subprocess, socket
#import cgroups

def start_mjpg_streamer():
    print("Starting up mjpg_streamer.")
    subprocess.run(["mjpg_streamer", "-i",
        "input_opencv.so -r 640x480 --filter /usr/lib/mjpg-streamer/cvfilter_py.so --fargs " + os.path.realpath(__file__),
        "-o",
        "output_http.so -p 8090 -w /usr/share/mjpg-streamer/www"])
        #stdin=subprocess.PIPE,
        #stdout=subprocess.PIPE,
        #stderr=subprocess.PIPE)
    # TODO: Add notification if either mjpg-streamer or cvfilter_py.so aren't installed
    # TODO: Detect any error if process exits, such as the uvcvideo crash I'm seeing

if __name__ == "__main__":
    start_mjpg_streamer()

def init_filter():
    # Display link to stream and dashboard
    print("Finding IP address...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]
    s.close()
    if not ip_addr:
        ip_addr = "localhost"
    print("Open http://" + str(ip_addr) + ":8090/?action=stream for video stream")
    print("Open http://" + str(ip_addr) + ":1880/ui for dashboard")
    print("Run bluedonkey_listen.sh to listen for messages")

    # Redirect input/output to a socket
    SOCK_OUT = 3001
    SOCK_IN = 3002
    sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock_out.connect(("255.255.255.255", SOCK_OUT))
    sys.stdout = sock_out.makefile('w', buffering=None)
    #errorfile = open("/tmp/bluedonkey.err.txt", 'w+')
    #sys.stderr = errorfile
    sys.stderr = sys.stdout
    sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_in.connect(("127.0.0.1", SOCK_IN))
    sys.stdin = sock_in.makefile('r', buffering=None)

    #cg = cgroups.Cgroup('bluedonkey')
    #pid  = os.getpid()
    #cg.add(pid)
    #cg.set_cpu_limit(50)
    import line_follower
    dc = dummy_car_control()
    f = line_follower.mjs_filter(dc)
    print("Returning process")
    return f.process

class dummy_car_control():
    def __init__(self):
        import car_control
        self.c = car_control.car_control()

    def tick(self):
        self.c.tick()
        return

    def update(self, line, threshold):
        (paused, throttle, steering, fps) = self.c.update(line)
        if paused:
            print("P ", end="", flush=False)
        else:
            print("  ", end="", flush=False)
        if line:
            print("%03d %03d " % (line[2], line[3]), end="", flush=False)
        else:
            print("No line ", end="", flush=False)
        print("%06.2f %06.2f" % (throttle, steering), end="", flush=False)
        print(" %04.1f" % (fps), end="", flush=False)
        print(" %03d" % (threshold), end="", flush=False)
        print("\r", end="", flush=True)
        return ""

