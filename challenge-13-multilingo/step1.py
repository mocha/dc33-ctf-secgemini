#!/usr/bin/env python3
import sys

flag = sys.stdin.readline().strip()
top = [(ord(char) & 0x80) >> 7 for char in flag]

if len(flag) != 29:
    sys.exit(1)

if sum(top) == 0:
    sys.exit(0)
else:
    sys.exit(1)
