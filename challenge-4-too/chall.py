#!/usr/bin/env python3
from flag import flag
from functools import reduce
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

keys = [get_random_bytes(16) for _ in range(16)]
flag = flag.encode() + b" " * (-len(flag) % 16)
for i in range(16):
    flag = AES.new(keys[i], AES.MODE_ECB).encrypt(flag)
x, y = [], []
for i in range(16):
    f = list(keys[i])
    g = lambda a, i: a[i % len(a)]
    h = range(len(f))
    k = lambda x, y: x ^ y
    r = lambda a: reduce(k, a)
    t = [r(g(f, i + x) for x in range(3)) for i in h]
    u = [r(g(t, i + x) for x in [0, 2, 4]) for i in h]
    x.append([r([g(t, i), g(t, i + 3), g(f, i + 3)]) for i in h])
    y.append(u)
print(f"{flag = }")
print(f"{x = }")
print(f"{y = }")
