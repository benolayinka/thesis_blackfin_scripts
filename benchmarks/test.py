import subprocess
import asyncio
make = subprocess.Popen([r"C:\Analog Devices\Crosscore Embedded Studio 2.8.3\Make.exe", "all", "-C", r"C:\Users\teenage\cces\2.8.3\benchmarks\Debug"], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
make.wait(timeout=90)
