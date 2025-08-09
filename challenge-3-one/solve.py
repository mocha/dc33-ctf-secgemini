#!/usr/bin/env python3

import struct
from pathlib import Path


STEPS = 20


def rotl(value: int, shift: int) -> int:
    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF


def rotr(value: int, shift: int) -> int:
    return ((value >> shift) | (value << (32 - shift))) & 0xFFFFFFFF


def qr(a: int, b: int, c: int, d: int):
    a = (a + b) & 0xFFFFFFFF
    d ^= a
    d = rotl(d, 16)
    c = (c + d) & 0xFFFFFFFF
    b ^= c
    b = rotl(b, 12)
    a = (a + b) & 0xFFFFFFFF
    d ^= a
    d = rotl(d, 8)
    c = (c + d) & 0xFFFFFFFF
    b ^= c
    b = rotl(b, 7)
    return a, b, c, d


def iqr(a: int, b: int, c: int, d: int):
    # Inverse of qr: reverse operations and use right rotations/subtraction
    b = rotr(b, 7)
    b ^= c
    c = (c - d) & 0xFFFFFFFF
    d = rotr(d, 8)
    d ^= a
    a = (a - b) & 0xFFFFFFFF
    b = rotr(b, 12)
    b ^= c
    c = (c - d) & 0xFFFFFFFF
    d = rotr(d, 16)
    d ^= a
    a = (a - b) & 0xFFFFFFFF
    return a, b, c, d


def dance(x: list[int]) -> list[int]:
    x = x[:]  # copy
    for _ in range(0, STEPS, 2):
        x[0], x[4], x[8], x[12] = qr(x[0], x[4], x[8], x[12])
        x[5], x[9], x[13], x[1] = qr(x[5], x[9], x[13], x[1])
        x[10], x[14], x[2], x[6] = qr(x[10], x[14], x[2], x[6])
        x[15], x[3], x[7], x[11] = qr(x[15], x[3], x[7], x[11])
        x[0], x[1], x[2], x[3] = qr(x[0], x[1], x[2], x[3])
        x[5], x[6], x[7], x[4] = qr(x[5], x[6], x[7], x[4])
        x[10], x[11], x[8], x[9] = qr(x[10], x[11], x[8], x[9])
        x[15], x[12], x[13], x[14] = qr(x[15], x[12], x[13], x[14])
    return x


def undance(x: list[int]) -> list[int]:
    x = x[:]  # copy
    for _ in range(0, STEPS, 2):
        # reverse the order of quarter rounds and apply inverse
        x[15], x[12], x[13], x[14] = iqr(x[15], x[12], x[13], x[14])
        x[10], x[11], x[8], x[9] = iqr(x[10], x[11], x[8], x[9])
        x[5], x[6], x[7], x[4] = iqr(x[5], x[6], x[7], x[4])
        x[0], x[1], x[2], x[3] = iqr(x[0], x[1], x[2], x[3])
        x[15], x[3], x[7], x[11] = iqr(x[15], x[3], x[7], x[11])
        x[10], x[14], x[2], x[6] = iqr(x[10], x[14], x[2], x[6])
        x[5], x[9], x[13], x[1] = iqr(x[5], x[9], x[13], x[1])
        x[0], x[4], x[8], x[12] = iqr(x[0], x[4], x[8], x[12])
    return x


def words_from_bytes_be(b: bytes) -> list[int]:
    return [struct.unpack(">I", b[i : i + 4])[0] for i in range(0, len(b), 4)]


def bytes_from_words_be(words: list[int]) -> bytes:
    return b"".join(struct.pack(">I", w) for w in words)


def recover_key_and_nonce(keystream_block0: bytes):
    state_out = words_from_bytes_be(keystream_block0)
    initial_state = undance(state_out)

    const_words = [
        struct.unpack(">I", b"expa")[0],
        struct.unpack(">I", b"nd 3")[0],
        struct.unpack(">I", b"2-by")[0],
        struct.unpack(">I", b"te k")[0],
    ]
    assert initial_state[0:4] == const_words, "Unexpected constants in state; inversion likely wrong"
    assert initial_state[12] == 0 and initial_state[13] == 0, "Counter for first block should be zero"

    key_words = initial_state[4:12]
    nonce_words = initial_state[14:16]
    key = bytes_from_words_be(key_words)
    nonce = bytes_from_words_be(nonce_words)
    return key, nonce


def generate_keystream_block(key: bytes, nonce: bytes, counter: int) -> bytes:
    state = [0] * 16
    state[0] = struct.unpack(">I", b"expa")[0]
    state[1] = struct.unpack(">I", b"nd 3")[0]
    state[2] = struct.unpack(">I", b"2-by")[0]
    state[3] = struct.unpack(">I", b"te k")[0]
    for idx in range(8):
        state[4 + idx] = struct.unpack(">I", key[4 * idx : 4 * idx + 4])[0]
    state[12] = (counter >> 32) & 0xFFFFFFFF
    state[13] = counter & 0xFFFFFFFF
    state[14] = struct.unpack(">I", nonce[0:4])[0]
    state[15] = struct.unpack(">I", nonce[4:8])[0]

    out_state = dance(state)
    return bytes_from_words_be(out_state)


def main():
    data_path = Path(__file__).with_name("out.txt")
    ct = bytes.fromhex(data_path.read_text().strip())

    # First block is 64 bytes; plaintext there is all 'A's
    ct0, ct_rest = ct[:64], ct[64:]
    ks0 = bytes(c ^ 0x41 for c in ct0)  # 'A' == 0x41

    key, nonce = recover_key_and_nonce(ks0)

    # Decrypt remaining bytes with as many keystream blocks as needed
    plaintext_rest = bytearray()
    offset = 64
    while offset < len(ct):
        ks = generate_keystream_block(key, nonce, counter=offset)
        chunk = ct[offset : offset + 64]
        plaintext_rest.extend(bytes(c ^ k for c, k in zip(chunk, ks)))
        offset += 64

    print(plaintext_rest.decode(errors="ignore"))


if __name__ == "__main__":
    main()


