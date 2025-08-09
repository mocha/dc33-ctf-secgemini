#!/usr/bin/env python3
import struct
import hashlib
import hmac
from typing import Tuple, List

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


MAGIC = b"PCTF"
STBL = b"STBL"
FLAG = b"FLAG"


def kdf_42x_sha256(seed12: bytes) -> bytes:
    """Repeatedly hash seed12 (or the previous hash output) 42 times; return final 32-byte hash."""
    assert len(seed12) == 12
    data = seed12
    for _ in range(42):
        data = hashlib.sha256(data).digest()
    return data


def derive_key_iv(seed12: bytes) -> Tuple[bytes, bytes]:
    h = kdf_42x_sha256(seed12)
    # Per spec: lower 16 bytes => key, upper 16 bytes => iv
    return h[:16], h[16:]


def aes128_ctr_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


def brute_force_pin_and_decrypt_outer(blob: bytes) -> bytes:
    # Header: magic(4) + length(4 little endian)
    assert blob[:4] == MAGIC, "Bad magic"
    length = struct.unpack("<I", blob[4:8])[0]
    assert len(blob) == 8 + length, "Length field mismatch"

    header8 = blob[:8]
    ciphertext = blob[8:]

    for pin in range(10000):
        pin_ascii = f"{pin:04d}".encode()
        seed12 = pin_ascii + header8
        key, iv = derive_key_iv(seed12)
        plaintext = aes128_ctr_decrypt(ciphertext, key, iv)
        mac = plaintext[:32]
        rest = plaintext[32:]
        check = hmac.new(key, rest, hashlib.sha256).digest()
        if hmac.compare_digest(mac, check):
            return plaintext

    raise RuntimeError("PIN not found")


def parse_outer_plaintext(plaintext: bytes) -> Tuple[bytes, bytes]:
    body = plaintext[32:]
    assert body[:4] == STBL, "Missing STBL header"
    table_len = struct.unpack("<I", body[4:8])[0]
    table = body[8:8 + table_len]

    pos = 8 + table_len
    assert body[pos:pos + 4] == FLAG, "Missing FLAG header"
    pos += 4
    indices_len = struct.unpack("<I", body[pos:pos + 4])[0]
    pos += 4
    indices_cipher = body[pos:pos + indices_len]
    return table, indices_cipher


def decrypt_indices(indices_cipher: bytes) -> List[int]:
    # Use the reference 12-byte passphrase from the spec
    passphrase = bytes.fromhex("f917db0091ff88a0b4836599")
    assert len(passphrase) == 12
    key, iv = derive_key_iv(passphrase)
    indices_plain = aes128_ctr_decrypt(indices_cipher, key, iv)

    # Interpret as array of little-endian uint16
    if len(indices_plain) % 2 != 0:
        raise ValueError("Indices length not even")
    return list(struct.unpack("<" + "H" * (len(indices_plain) // 2), indices_plain))


def reconstruct_flag(table: bytes, indices: List[int]) -> str:
    chars = []
    for idx in indices:
        if idx >= len(table):
            raise IndexError(f"Index {idx} out of table range {len(table)}")
        chars.append(chr(table[idx]))
    return "".join(chars)


def solve(path: str) -> str:
    blob = open(path, "rb").read()
    outer_plain = brute_force_pin_and_decrypt_outer(blob)
    table, indices_cipher = parse_outer_plaintext(outer_plain)
    indices = decrypt_indices(indices_cipher)
    return reconstruct_flag(table, indices)


if __name__ == "__main__":
    print(solve("flag.ctf"))


