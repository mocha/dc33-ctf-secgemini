#!/usr/bin/env python3

import os
import struct
from secrets import FLAG

STEPS = 20

def rotl(v, s):
    return ((v << s) | (v >> (32 - s))) & 0xffffffff

def qr(a, b, c, d):
    a = (a + b) & 0xffffffff
    d ^= a
    d = rotl(d, 16)
    c = (c + d) & 0xffffffff
    b ^= c
    b = rotl(b, 12)
    a = (a + b) & 0xffffffff
    d ^= a
    d = rotl(d, 8)
    c = (c + d) & 0xffffffff
    b ^= c
    b = rotl(b, 7)
    return a, b, c, d

def dance(x):
    for i in range(0, STEPS, 2):
        x[ 0], x[ 4], x[ 8], x[12] = qr(x[ 0], x[ 4], x[ 8], x[12])
        x[ 5], x[ 9], x[13], x[ 1] = qr(x[ 5], x[ 9], x[13], x[ 1])
        x[10], x[14], x[ 2], x[ 6] = qr(x[10], x[14], x[ 2], x[ 6])
        x[15], x[ 3], x[ 7], x[11] = qr(x[15], x[ 3], x[ 7], x[11])
        x[ 0], x[ 1], x[ 2], x[ 3] = qr(x[ 0], x[ 1], x[ 2], x[ 3])
        x[ 5], x[ 6], x[ 7], x[ 4] = qr(x[ 5], x[ 6], x[ 7], x[ 4])
        x[10], x[11], x[ 8], x[ 9] = qr(x[10], x[11], x[ 8], x[ 9])
        x[15], x[12], x[13], x[14] = qr(x[15], x[12], x[13], x[14])
    return x

def encrypt(plaintext, key, nonce):
    ciphertext = b""

    for i in range(0, len(plaintext), 64):
        state = [0] * 16
        state[ 0] = struct.unpack(">I", b"expa")[0]
        state[ 1] = struct.unpack(">I", b"nd 3")[0]
        state[ 2] = struct.unpack(">I", b"2-by")[0]
        state[ 3] = struct.unpack(">I", b"te k")[0]
        state[ 4] = struct.unpack(">I", key[0:4])[0]
        state[ 5] = struct.unpack(">I", key[4:8])[0]
        state[ 6] = struct.unpack(">I", key[8:12])[0]
        state[ 7] = struct.unpack(">I", key[12:16])[0]
        state[ 8] = struct.unpack(">I", key[16:20])[0]
        state[ 9] = struct.unpack(">I", key[20:24])[0]
        state[10] = struct.unpack(">I", key[24:28])[0]
        state[11] = struct.unpack(">I", key[28:32])[0]
        state[12] = (i >> 32) & 0xffffffff
        state[13] = i & 0xffffffff
        state[14] = struct.unpack(">I", nonce[0:4])[0]
        state[15] = struct.unpack(">I", nonce[4:8])[0]

        state = dance(state)

        keystream = b""
        for j in range(16):
            keystream += struct.pack(">I", state[j])

        ciphertext += bytes(a ^ b for a, b in zip(keystream, plaintext[i:i+64]))

    return ciphertext

key = os.urandom(32)
nonce = os.urandom(8)
plaintext = (b"A" * 64) + FLAG
ciphertext = encrypt(plaintext, key, nonce)
print(ciphertext.hex())
