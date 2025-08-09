#!/usr/bin/env python3

from typing import List, Optional


MOD = 256


def to_u8(value: int) -> int:
    return value % MOD


def inverse_transform_byte(y: int) -> int:
    # Inverse of: y = ((((x + 0x77) * 0x55) ^ 0x33) - 0x11) mod 256
    # inv(0x55) mod 256 is 0xFD (253) because 256 - 3 = 253 and 85 * 253 ≡ 1 (mod 256)
    return to_u8(((y + 0x11) ^ 0x33) * 0xFD - 0x77)


def solve_transformed_flag() -> List[int]:
    y: List[Optional[int]] = [None] * 64

    # Single-byte equality constraints from chal.c
    singles = {
        32: 0x43,
        36: 0x29,
        40: 0x76,
        48: 0x2C,
        8: 0x70,
        4: 0x25,
        44: 0x70,
        16: 0x40,
        56: 0x2E,
        20: 0x7B,
        12: 0xE2,
        0: 0xE0,
        60: 0x25,
        24: 0x23,
        28: 0x40,
        52: 0x2C,
    }
    for idx, val in singles.items():
        y[idx] = val

    # Pairwise XOR constraints: (a ^ b) == c
    xor_pairs = [
        (48, 49, 0x5C),
        (32, 33, 0x1E),
        (0, 1, 0xA3),
        (28, 29, 0x3C),
        (12, 13, 0xCB),
        (60, 61, 0x60),
        (36, 37, 0x0A),
        (56, 57, 0x41),
        (24, 25, 0x13),
        (52, 53, 0x5C),
        (4, 5, 0x60),
        (8, 9, 0x5F),
        (16, 17, 0x9F),
        (44, 45, 0x5C),
        (40, 41, 0x0C),
        (20, 21, 0x39),
    ]

    # Triple XOR constraints: (a ^ b ^ c) == d
    xor_triples = [
        (37, 38, 39, 0x7F),
        (9, 10, 11, 0x05),
        (61, 62, 63, 0x46),
        (13, 14, 15, 0x11),
        (25, 26, 27, 0x6F),
        (21, 22, 23, 0x78),
        (29, 30, 31, 0x25),
        (57, 58, 59, 0x31),
        (17, 18, 19, 0xC6),
        (33, 34, 35, 0x1D),
        (49, 50, 51, 0x70),
        (1, 2, 3, 0xFA),
        (45, 46, 47, 0x6A),
        (5, 6, 7, 0x4C),
        (41, 42, 43, 0x62),
        (53, 54, 55, 0x1B),
    ]

    # Sum-difference constraints: ((a - b + c) & 0xFF) == d
    sumdiff = [
        (20, 21, 23, 0xB3),
        (52, 53, 55, 0xEC),
        (60, 61, 63, 0x06),
        (16, 17, 19, 0xD0),
        (40, 41, 43, 0x2C),
        (48, 49, 51, 0xEB),
        (36, 37, 39, 0x32),
        (32, 33, 35, 0x20),
        (44, 45, 47, 0x74),
        (28, 29, 31, 0x34),
        (56, 57, 59, 0xEB),
        (24, 25, 27, 0x1F),
        (4, 5, 7, 0x0C),
        (8, 9, 11, 0xB2),
        (0, 1, 3, 0xF5),
        (12, 13, 15, 0xE5),
    ]

    progress = True
    while progress:
        progress = False

        # Use pair XORs where one is known
        for a, b, vxor in xor_pairs:
            if y[a] is not None and y[b] is None:
                y[b] = y[a] ^ vxor
                progress = True
            elif y[b] is not None and y[a] is None:
                y[a] = y[b] ^ vxor
                progress = True

        # Use sum-diff where two are known -> solve the third
        for a, b, c, target in sumdiff:
            ya, yb, yc = y[a], y[b], y[c]
            if ya is not None and yb is not None and yc is None:
                y[c] = to_u8(target - (ya - yb))
                progress = True
            elif ya is not None and yc is not None and yb is None:
                # (a - b + c) == target  =>  b == a + c - target
                y[b] = to_u8(ya + yc - target)
                progress = True
            elif yb is not None and yc is not None and ya is None:
                # (a - b + c) == target  =>  a == target + b - c
                y[a] = to_u8(target + yb - yc)
                progress = True

        # Use triple XORs where two are known
        for a, b, c, vxor in xor_triples:
            ya, yb, yc = y[a], y[b], y[c]
            if ya is not None and yb is not None and yc is None:
                y[c] = ya ^ yb ^ vxor
                progress = True
            elif ya is not None and yc is not None and yb is None:
                y[b] = ya ^ yc ^ vxor
                progress = True
            elif yb is not None and yc is not None and ya is None:
                y[a] = yb ^ yc ^ vxor
                progress = True

    if any(v is None for v in y):
        missing = [i for i, v in enumerate(y) if v is None]
        raise RuntimeError(f"Unresolved positions in y: {missing}")

    return [int(v) for v in y]


def invert_to_original_bytes(transformed: List[int]) -> bytes:
    original_bytes = bytes(inverse_transform_byte(b) for b in transformed)
    return original_bytes


def main() -> None:
    y = solve_transformed_flag()
    x_bytes = invert_to_original_bytes(y)

    # Ensure length 64
    assert len(x_bytes) == 64

    # Print the candidate flag and also a hex preview
    try:
        candidate = x_bytes.decode('utf-8', errors='strict')
    except Exception:
        candidate = x_bytes.decode('latin1')

    print(candidate)


if __name__ == "__main__":
    main()


