import sys
from cpu import *

cpu = CPU(sys.argv[1])

cpu.load()
cpu.run()