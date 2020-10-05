#!/usr/bin/env python
#
# Simple program to measure system responsiveness

from datetime import datetime as dt
from time import sleep

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

spinner = spinning_cursor()
while True:
    start = dt.now()
    sleep(1)
    delta = dt.now() - start
    print("%c delta_t = %d" %(next(spinner), int(delta.total_seconds() * 1000)))
