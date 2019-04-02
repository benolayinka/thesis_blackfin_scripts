import subprocess
import time
import asyncio
import sys
import time
import re
import json
import os

tests = r"tests.txt"
cfile = r"C:\Users\teenage\cces\2.8.3\bf706ez\src\bf706ez.c"
from generatetests import generate_tests
try:
    os.replace(cfile, cfile+'old')
except: pass
generate_tests(tests, cfile)

WATCHDOG = 90 #maximum number of samples (seconds) - useful if bf hangs

asyncio.set_event_loop_policy(
    asyncio.WindowsProactorEventLoopPolicy())

test_fn = r"C:\Users\teenage\cces\2.8.3\bf706ez\src\test.h"

timestr = time.strftime("%Y%m%d-%H%M%S")
power_measurements_fn = "sim_" + timestr + ".json"

current_regex = '\d+mA'

all_tests_dict = []

for i in range(0, 100):
    with open(test_fn, 'w') as f:
        f.write("#define TEST " + str(i) + "\n")
        f.write("#define SIM 1\n")

    test_results = {}

    try:
        os.replace(r'C:\Users\teenage\cces\2.8.3\bf706ez\Debug\bf706ez.dxe', r'C:\Users\teenage\cces\2.8.3\bf706ez\Debug\bf706ezold.dxe')
    except:
        pass

    print('launching make process, test# ' + str(i))
    
    try:
        make = subprocess.Popen([r"C:\Analog Devices\Crosscore Embedded Studio 2.8.3\Make.exe", "all", "-C", r"C:\Users\teenage\cces\2.8.3\bf706ez\Debug"], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        make.wait(timeout=WATCHDOG)
        test_results["make_stdout"] = make.stdout.read().decode()
        test_results["make_stderr"] = make.stderr.read().decode()

        if (test_results["make_stderr"]):
            print('error in make, skipping test')
            all_tests_dict.append(test_results)
            continue
        
    except Exception as e:
        print('error in make')
        print(e)
        break

    print('launching cces process, test# ' + str(i))

    try:
        cces_runner = subprocess.Popen([r"C:\Analog Devices\Crosscore Embedded Studio 2.8.3\CCES_runner.exe", "-@", "options_sim.txt"], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        cces_runner.wait(timeout=WATCHDOG)

        out = cces_runner.stdout.read().decode()
        test_results["cces_runner_stdout"] = out
        test_results["cces_runner_stderr"] = cces_runner.stderr.read().decode()

        if (test_results["cces_runner_stderr"]):
            print('error in runner, ending tests')
            all_tests_dict.append(test_results)
            break

        test_results["name"] = out.split(sep=" cycles")[0]
        out = out.split("cycles:")[1]
        test_results["cycles"] = int(out.split()[0])

        all_tests_dict.append(test_results)
        
    except Exception as e:
        print('error in cces process')
        print(e)
        if cces_runner: cces_runner.kill()
        all_tests_dict.append(test_results)
        break

    if test_results["name"] == 'end':
        break

    
with open(power_measurements_fn, 'w') as outfile:
    json.dump(all_tests_dict, outfile)
    print('data dumped to ' + power_measurements_fn)
