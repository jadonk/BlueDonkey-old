#!/usr/bin/env python3.7
import os, sys, subprocess, socket, cgroups

def start_mjpg_streamer():
    # Redirect input/output to a socket
    SOCK_OUT = 3001
    SOCK_IN = 3002
    sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock_out.connect(("255.255.255.255", SOCK_OUT))
    sys.stdout = sock_out.makefile('w', buffering=None)
    errorfile = open("/tmp/bluedonkey.err.txt", 'w+')
    sys.stderr = errorfile
    #sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock_in.connect(("127.0.0.1", SOCK_IN))
    #sys.stdin = sock_in.makefile('r', buffering=None)

    print("Starting up mjpg_streamer.")
    subprocess.run(["mjpg_streamer", "-i",
        "input_opencv.so -r 640x480 --filter /usr/local/lib/mjpg-streamer/cvfilter_py.so --fargs " + os.path.realpath(__file__),
        "-o",
        "output_http.so -p 8090 -w /usr/share/mjpg-streamer/www"])
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    start_mjpg_streamer()

def init_filter():
    cg = cgroups.Cgroup('bluedonkey')
    pid  = os.getpid()
    cg.add(pid)
    cg.set_cpu_limit(50)
    import line_follower
    f = line_follower.mjs_filter()
    return f.process
