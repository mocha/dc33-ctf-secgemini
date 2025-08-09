#!/usr/bin/env python3
"""
Recover AES keys from the custom keyless cipher (x, y arrays) and decrypt the flag.

Given, for each key bytes array f[0..15]:
  t[i] = f[i] ^ f[i+1] ^ f[i+2]
  u[i] = t[i] ^ t[i+2] ^ t[i+4]   -> this is provided as y[i]
  x[i] = t[i] ^ t[i+3] ^ f[i+3]   -> this is provided as x[i]

We solve the linear system for t from u (size 16 over GF(2) per bit using XOR), then recover f.
Finally, we decrypt the ciphertext by applying AES-ECB decryption with the recovered keys
in reverse order.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List

from Crypto.Cipher import AES


WORKDIR = Path(__file__).resolve().parent


def parse_output_file(path: Path):
    text = path.read_text()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    flag_bytes = ast.literal_eval(lines[0].split("=", 1)[1].strip())
    x_lists = ast.literal_eval(lines[1].split("=", 1)[1].strip())
    y_lists = ast.literal_eval(lines[2].split("=", 1)[1].strip())
    return flag_bytes, x_lists, y_lists


def solve_linear_system_for_t(u_values: List[int]) -> List[int]:
    """Solve A * t = u over GF(2) where A[i,j] = 1 if j in {i, i+2, i+4} (mod 16).

    We operate on bytes directly since XOR is bitwise and linear.
    Returns list t[0..15] as integers 0..255.
    """
    n = 16
    # Represent each row by a 16-bit mask. Column j corresponds to bit (1 << j).
    rows = [((1 << i) | (1 << ((i + 2) % n)) | (1 << ((i + 4) % n))) for i in range(n)]
    b = u_values[:]  # right-hand side (bytes)

    # Forward elimination to row-echelon form
    pivot_cols = []  # pivot column index for each row in order
    row_idx = 0
    for col in range(n):
        # Find pivot row with a 1 in this column at or below row_idx
        pivot = None
        for r in range(row_idx, n):
            if (rows[r] >> col) & 1:
                pivot = r
                break
        if pivot is None:
            # Should not happen for invertible A, but keep robust
            continue
        # Swap pivot row into position
        if pivot != row_idx:
            rows[row_idx], rows[pivot] = rows[pivot], rows[row_idx]
            b[row_idx], b[pivot] = b[pivot], b[row_idx]
        # Eliminate below
        for r in range(row_idx + 1, n):
            if (rows[r] >> col) & 1:
                rows[r] ^= rows[row_idx]
                b[r] ^= b[row_idx]
        pivot_cols.append(col)
        row_idx += 1
        if row_idx == n:
            break

    # Back substitution to reduced row-echelon form
    for i in range(len(pivot_cols) - 1, -1, -1):
        col = pivot_cols[i]
        # Find the row index i (already aligned by construction)
        for r in range(0, i):
            if (rows[r] >> col) & 1:
                rows[r] ^= rows[i]
                b[r] ^= b[i]

    # Map solution bytes to their respective columns
    t = [0] * n
    for i, col in enumerate(pivot_cols):
        t[col] = b[i]

    if any(val == 0 and ((rows[i] & (1 << pivot_cols[i])) == 0) for i, val in enumerate(t[: len(pivot_cols)])):
        # Very defensive; matrix should be invertible, but keep a clear error if not
        raise ValueError("Singular system encountered while solving for t")

    return t


def recover_key_from_xy(x_vals: List[int], y_vals: List[int]) -> bytes:
    t = solve_linear_system_for_t(y_vals)
    f = [0] * 16
    for k in range(16):
        j = (k - 3) % 16
        f[k] = x_vals[j] ^ t[j] ^ t[k]
    return bytes(f)


def main():
    flag_bytes, x_lists, y_lists = parse_output_file(WORKDIR / "output.txt")

    # Recover all 16 keys (same order as used in encryption)
    recovered_keys = [recover_key_from_xy(x_lists[i], y_lists[i]) for i in range(16)]

    # Decrypt layers in reverse order
    plaintext = flag_bytes
    for i in range(15, -1, -1):
        cipher = AES.new(recovered_keys[i], AES.MODE_ECB)
        plaintext = cipher.decrypt(plaintext)

    print(plaintext.rstrip(b" ").decode(errors="replace"))


if __name__ == "__main__":
    main()


