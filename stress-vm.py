#!/usr/bin/env python3

import re
import random
import time
import sys
from math import ceil
from datetime import datetime

def get_mem_usage():
    pattern = re.compile(r'^(.*):[\s]*([\d]+)[\s]*(.B).*$')
    mem_total = None
    mem_free = None
    bytes_by_units = {'kB': 1024}
    lines = [line.strip('\n') for line in open('/proc/meminfo')]
    for line in lines:
        matches = pattern.fullmatch(line)
        if not matches:
            continue
        if 'MemTotal' == matches.group(1):
            mem_total = int(matches.group(2)) * bytes_by_units[matches.group(3)]
        elif 'MemFree' == matches.group(1):
            mem_free = int(matches.group(2)) * bytes_by_units[matches.group(3)]
    return mem_free, mem_total

def allocate_random_array(num_bytes):
    return tuple(random.getrandbits(64) for _ in range(ceil(num_bytes / 64)))

def allocate_ram_perc(target_pct):
    data = []
    start_ts = time.time()
    while True:
        mem_free, mem_total = get_mem_usage()
        alloc_pct = int(((mem_total - mem_free) / mem_total) * 100)
        curr_ts = time.time()
        print('time={:.2f} total={} free={} alloc {}% target {}%'.format(curr_ts - start_ts, mem_total, mem_free, alloc_pct, target_pct))
        if alloc_pct >= target_pct:
            break
        else:
            data.append(allocate_random_array(int(mem_total / 100)))
    return data

def do_some_array_math(data):
    return (sum(i) for i in data)

def spinning_cursor():
    while True:
        for cursor in '|/-':
            yield cursor

def main():
    data = allocate_ram_perc(int(sys.argv[1]))
    sys.stdout.write("done ")
    sys.stdout.flush()
    spinner = spinning_cursor()
    while True:
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        do_some_array_math(data)
        time.sleep(0.25)
        sys.stdout.write('\b')

if __name__ == '__main__':
    main()
