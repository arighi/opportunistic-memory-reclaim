#!/usr/bin/env python3
#
# User-space script to monitor system idle % and trigger opportunistic memory
# reclaim.

import sys
import json
import shlex
from subprocess import Popen, PIPE
from time import sleep, time

# Configuration settings
#
# TODO: move this to a config file

# Debugging enabled/disabled
DEBUG = True

# If system idle % is > IDLE_THRESHOLD_PERC for more than
# IDLE_THRESHOLD_TIME_SEC => trigger memory reclaim; system idle % is checked
# every IDLE_POLLING_TIME_SEC.
IDLE_THRESHOLD_PERC = 95
IDLE_THRESHOLD_TIME_SEC = 30
IDLE_POLLING_TIME_SEC = 1

# Kernel ABI (pass a different file to the cmdline if reclaiming memory of a
# specific cgroup, otherwise perform system-wide memory reclaim.
try:
    MM_RECLAIM = sys.argv[1]
except:
    MM_RECLAIM = '/sys/fs/cgroup/memory.swap.reclaim'

# Trigger opportunistic memory reclaim
def do_memory_reclaim():
    try:
        with open(MM_RECLAIM, 'w') as f:
            f.write("max\n")
    except:
        sys.stderr.write("WARNING: couldn't write to %s\n" % MM_RECLAIM)
        sys.stderr.flush()

# Return the minimum idle% across all CPUs
def get_min_idle():
    cmd = 'mpstat -P ALL -o JSON 1 1'
    output = Popen(shlex.split(cmd), stdout=PIPE).communicate()[0]
    data = json.loads(output)
    cpu_idle = data["sysstat"]["hosts"][0]["statistics"][0]["cpu-load"]
    if DEBUG:
        debug_idle = {}
        for c in cpu_idle:
            if c["cpu"] != "all":
                debug_idle[c["cpu"]] = c["idle"]
        print(json.dumps(debug_idle))

    return min([c["idle"] for c in cpu_idle if c["cpu"] != "all"])

# Main
def main():
    start_time = time()
    while True:
        now = time()
        try:
            min_idle = get_min_idle()
        except:
            min_idle = 0
        if min_idle < IDLE_THRESHOLD_PERC:
            start_time = now
        else:
            if now - start_time > IDLE_THRESHOLD_TIME_SEC:
                print(">>> trigger memory reclaim")
                do_memory_reclaim()
                start_time = now
        sleep(IDLE_POLLING_TIME_SEC)

if __name__ == '__main__':
    main()
