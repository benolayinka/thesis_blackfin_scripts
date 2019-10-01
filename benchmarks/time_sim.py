import subprocess
import time
import asyncio
import sys
import time
import re
import json
import os

loops = 1
WATCHDOG = 90

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def stddev(data, ddof=0):
    """Calculates the population standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/(n-ddof)
    return pvar**0.5

def stddev(data, ddof=0):
	return 0


total_time = []


for _ in range(loops):
    start_time = time.time()
    make = subprocess.Popen([r"C:\Analog Devices\Crosscore Embedded Studio 2.8.3\Make.exe", "all", "-C", r"C:\Users\teenage\cces\2.8.3\benchmarks\Debug"], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    make.wait(timeout=WATCHDOG)
    total_time.append(time.time()-start_time)

mean_time = mean(total_time)
std = stddev(total_time)
print("Make & %s & %d & %d" % (mean_time, loops, std))
total_time = []

for _ in range(loops):
    start_time = time.time()
    cces_runner = subprocess.Popen([r"C:\Analog Devices\Crosscore Embedded Studio 2.8.3\CCES_runner.exe", "-@", "options_sim.txt"], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    cces_runner.wait(timeout=WATCHDOG)
    total_time.append(time.time()-start_time)

mean_time = mean(total_time)
std = stddev(total_time)
print("Sim & %s & %d & %d" % (mean_time, loops, std))
total_time = []
