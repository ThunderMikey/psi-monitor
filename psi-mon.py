#!/usr/bin/env python3
from enum import Enum
from abc import ABC, abstractmethod
from queue import Queue
from time import sleep
import sys, re

# in seconds
POLL_INTERVAL = float(sys.argv[1])
SEC_IN_USEC = 1000000000

class PsiType(Enum):
    SOME = 1
    FULL = 2

class XPsi(ABC):
    @abstractmethod
    def __init__(self):
        self.path = "/dev/null"

    def get_x_total_usec(self, x: PsiType):
        with open(self.path, 'r') as f:
            # first line is "some", second line is "full"
            result = str(f.read()).strip().split("\n")
            if (x == PsiType.SOME):
                line = result[0]
            elif (x == PsiType.FULL):
                line = result[1]
            else:
                RuntimeError("Unkown PsiType: {}".format(x))
            return float(re.search('total=(\d+)', line).group(1))

    def get_some_total_usec(self):
        return self.get_x_total_usec(PsiType.SOME)

    def get_full_total_usec(self):
        return self.get_x_total_usec(PsiType.FULL)

class CPUPsi(XPsi):
    def __init__(self):
        self.path = "/proc/pressure/cpu"

class IOPsi(XPsi):
    def __init__(self):
        self.path = "/proc/pressure/io"

class MemoryPsi(XPsi):
    def __init__(self):
        self.path = "/proc/pressure/memory"

cpu_psi = CPUPsi()
memory_psi = MemoryPsi()
io_psi = IOPsi()

# CPU PSI Queue
cp1 = cp0 = cpu_psi.get_some_total_usec()
# Memory PSI Queue
mp1 = mp0 = memory_psi.get_some_total_usec()
# IO PSI Queue
ip1 = ip0 = io_psi.get_some_total_usec()

def convert_percentage(num):
    return round(100*num/POLL_INTERVAL/SEC_IN_USEC, 5)

while True:
    cp1 = cpu_psi.get_some_total_usec()
    mp1 = memory_psi.get_some_total_usec()
    ip1 = io_psi.get_some_total_usec()
    cp = convert_percentage(cp1 - cp0)
    mp = convert_percentage(mp1 - mp0)
    ip = convert_percentage(ip1 - ip0)
    cp0 = cp1
    mp0 = mp1
    ip0 = ip1
    print("CPU: {}, Mem: {}, IO: {}".format(cp, mp, ip))
    sleep(POLL_INTERVAL)

