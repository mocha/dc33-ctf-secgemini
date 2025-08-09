#!/usr/bin/env python3
import base64
import hashlib
import sys


def compute_checksum(clicks_bytes: bytes) -> bytes:
    h = hashlib.sha256(clicks_bytes).digest()
    c = [0] * 8
    c[0] = (h[1] ^ h[0]) | h[24]
    c[2] = (h[3] ^ h[2]) | h[25]
    c[4] = (h[3] ^ h[4]) | h[26]
    c[6] = (h[7] ^ h[6]) | h[27]
    c[1] = (h[1] | h[2]) ^ h[28]
    c[3] = (h[3] | h[1]) ^ h[29]
    c[5] = (h[3] | h[1]) ^ h[30]
    c[7] = (h[7] | h[2]) ^ h[31]
    return bytes(c)


def make_save_state(clicks: int) -> str:
    if clicks < 1:
        raise ValueError("clicks must be >= 1")
    clicks_str = str(clicks)
    clicks_bytes = clicks_str.encode()
    checksum = compute_checksum(clicks_bytes)
    payload = clicks_bytes + checksum
    return base64.b64encode(payload).decode()


def main():
    # Default: use u128::MAX to cause 1 click overflow to 0 in release builds
    u128_max = (1 << 128) - 1
    clicks = u128_max
    if len(sys.argv) > 1:
        clicks = int(sys.argv[1])

    b64 = make_save_state(clicks)
    print(b64)

    # Quick usage hint
    sys.stderr.write(
        "\nPaste the above Base64 when choosing option 4 (load), then choose 1 (click), then 2 (claim).\n"
    )


if __name__ == "__main__":
    main()


