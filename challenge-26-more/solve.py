#!/usr/bin/env python3
import base64
import binascii
import os
import re
import sys
import zlib
from typing import Tuple

CHALLENGE_FILE = os.path.join(os.path.dirname(__file__), 'challenge.txt')
OUT_DIR = os.path.dirname(__file__)


def read_hex_from_challenge() -> str:
    with open(CHALLENGE_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    # Extract hex-like characters only
    hex_str = re.sub(r'[^0-9a-fA-F]', '', data)
    if len(hex_str) % 2 != 0:
        # Pad if odd length to avoid exceptions; shouldn't happen but be robust
        hex_str = hex_str[:-1]
    return hex_str


def xor_with_byte(data: bytes, key: int) -> bytes:
    return bytes(b ^ key for b in data)


def try_base64_decode(b: bytes) -> Tuple[bool, bytes]:
    b_stripped = re.sub(b'[^A-Za-z0-9+/=\n\r]', b'', b)
    # Ensure proper padding
    try:
        decoded = base64.b64decode(b_stripped, validate=False)
        # Heuristic: decoding should change length meaningfully
        if decoded and len(decoded) > 0 and len(decoded) != len(b):
            return True, decoded
    except Exception:
        pass
    return False, b


def try_hex_decode(b: bytes) -> Tuple[bool, bytes]:
    try:
        # Remove non-hex
        s = re.sub(b'[^0-9a-fA-F]', b'', b)
        if len(s) % 2 != 0:
            s = s[:-1]
        decoded = binascii.unhexlify(s)
        if decoded and len(decoded) > 0 and len(decoded) != len(b):
            return True, decoded
    except Exception:
        pass
    return False, b


def try_decompress(b: bytes) -> Tuple[bool, bytes, str]:
    # Try common formats quickly
    # zlib (raw)
    for wbits, label in [(zlib.MAX_WBITS, 'zlib'), (zlib.MAX_WBITS | 16, 'gzip'), (-zlib.MAX_WBITS, 'deflate')]:
        try:
            d = zlib.decompress(b, wbits)
            return True, d, label
        except Exception:
            pass
    # No luck
    return False, b, ''


def save_layer(n: int, b: bytes, note: str = '') -> str:
    fname = os.path.join(OUT_DIR, f'layer{n}.bin')
    with open(fname, 'wb') as f:
        f.write(b)
    if note:
        print(f'[+] Saved layer {n} ({note}) to {fname} ({len(b)} bytes)')
    else:
        print(f'[+] Saved layer {n} to {fname} ({len(b)} bytes)')
    return fname


def looks_printable(b: bytes) -> bool:
    try:
        s = b.decode('utf-8')
    except Exception:
        return False
    # Consider it printable if most chars are in standard printable range
    printable = sum(32 <= ord(ch) <= 126 or ch in '\n\r\t' for ch in s)
    return printable >= 0.9 * len(s) if s else False


def reverse_bits_in_byte(x: int) -> int:
    v = x
    v = ((v & 0xF0) >> 4) | ((v & 0x0F) << 4)
    v = ((v & 0xCC) >> 2) | ((v & 0x33) << 2)
    v = ((v & 0xAA) >> 1) | ((v & 0x55) << 1)
    return v


def extract_layer2_message(layer1_bytes: bytes) -> bytes:
    # Normalize: replace NULs with spaces for marker search
    txt = layer1_bytes.replace(b'\x00', b' ')
    # Case-insensitive search for the marker 'THE MESSAGE'
    m = re.search(rb"(?i)THE\s+MESSAGE", txt)
    if m:
        start = m.end()
        tail = txt[start:]
        # Keep only A-Z letters from the tail
        letters = re.findall(rb"[A-Z]", tail)
        sym = b''.join(letters)
        if len(sym) >= 50:  # sanity threshold
            return sym
    # Fallback: longest run of A-Zs in entire text
    runs = re.findall(rb"[A-Z]{40,}", txt)
    if runs:
        candidate = max(runs, key=len)
        return candidate.strip()
    return b''


def symbols_to_bitstream(sym_bytes: bytes, reverse_symbol_bits: bool) -> list:
    bits = []
    for ch in sym_bytes:
        if 65 <= ch <= 90:  # 'A'-'Z'
            val = ch - 65  # 0..25
            # 5-bit value
            b5 = [(val >> k) & 1 for k in (4, 3, 2, 1, 0)]  # MSB..LSB
            if reverse_symbol_bits:
                b5.reverse()
            bits.extend(b5)
        # ignore spaces/newlines and any other chars
    return bits


def bits_to_bytes(bits: list, bit_offset: int, reverse_byte_bits: bool, reverse_stream: bool) -> bytes:
    work = bits.copy()
    if reverse_stream:
        work.reverse()
    # Apply offset by dropping first N bits
    if bit_offset > 0 and bit_offset < len(work):
        work = work[bit_offset:]
    out = bytearray()
    for i in range(0, len(work) // 8 * 8, 8):
        b = 0
        for j in range(8):
            b = (b << 1) | work[i + j]
        if reverse_byte_bits:
            b = reverse_bits_in_byte(b)
        out.append(b)
    return bytes(out)


def brute_decode_layer2(sym: bytes) -> list:
    candidates = []
    for reverse_symbol_bits in (False, True):
        bits = symbols_to_bitstream(sym, reverse_symbol_bits)
        for bit_offset in range(8):
            for reverse_byte_bits in (False, True):
                for reverse_stream in (False, True):
                    out = bits_to_bytes(bits, bit_offset, reverse_byte_bits, reverse_stream)
                    score = sum(32 <= b <= 126 or b in (9, 10, 13) for b in out)
                    ratio = score / len(out) if out else 0
                    has_flag = b'CTF' in out or b'FLAG' in out or b'ctf' in out or b'flag' in out
                    candidates.append({
                        'reverse_symbol_bits': reverse_symbol_bits,
                        'bit_offset': bit_offset,
                        'reverse_byte_bits': reverse_byte_bits,
                        'reverse_stream': reverse_stream,
                        'ratio': ratio,
                        'data': out,
                        'has_flag': has_flag,
                    })
    # Prefer those with flags, then by ratio
    candidates.sort(key=lambda c: (c['has_flag'], c['ratio']), reverse=True)
    return candidates[:40]


def try_single_byte_xor_candidates(b: bytes, top_n: int = 5):
    scores = []
    for key in range(256):
        x = xor_with_byte(b, key)
        score = sum(32 <= c <= 126 or c in (9, 10, 13) for c in x)
        ratio = score / len(x) if x else 0
        has_flag = b'CTF' in x or b'FLAG' in x or b'{' in x or b'}' in x
        scores.append((ratio, has_flag, key, x))
    scores.sort(key=lambda t: (t[1], t[0]), reverse=True)
    return scores[:top_n]


def main():
    hex_str = read_hex_from_challenge()
    cipher = binascii.unhexlify(hex_str)
    print(f'[i] Read {len(cipher)} bytes from challenge hex')

    # Layer 1: OceanSalt-like simple XOR with 0xDF (based on hint and ciphertext patterns)
    layer1 = xor_with_byte(cipher, 0xDF)
    save_layer(1, layer1, 'XOR 0xDF')

    # Show a preview of printable
    preview = layer1[:256]
    try:
        print('[i] Layer1 preview (repr):', repr(preview.decode('utf-8', errors='replace')))
    except Exception:
        print('[i] Layer1 preview (raw bytes):', preview[:64])

    current = layer1
    step = 2

    # Attempt layer 2: extract the A-Z message and brute-force base32-like decode
    sym = extract_layer2_message(layer1)
    if sym:
        print(f'[i] Extracted layer2 symbol text length: {len(sym)}')
        print(f"[i] layer2 symbols preview: {sym[:80]!r}")
        # Save the raw symbols for reference
        with open(os.path.join(OUT_DIR, 'layer2_symbols.txt'), 'wb') as f:
            f.write(sym + b'\n')
        cands = brute_decode_layer2(sym)
        best_printed = False
        for idx, c in enumerate(cands, 1):
            data = c['data']
            note = (
                f"revSymBits={c['reverse_symbol_bits']} offset={c['bit_offset']} "
                f"revByteBits={c['reverse_byte_bits']} revStream={c['reverse_stream']} ratio={c['ratio']:.2f} flag={c['has_flag']}"
            )
            save_layer(step, data, f'layer2 candidate {idx}: {note}')
            # Print preview for top few
            if not best_printed:
                preview = data[:160]
                try:
                    print('[i] best candidate preview:', preview.decode('utf-8', errors='replace'))
                except Exception:
                    print('[i] best candidate preview (bytes):', preview)
                best_printed = True

            # NEW: try single-byte XOR brute
            xor_hits = try_single_byte_xor_candidates(data, top_n=5)
            for rank, (ratio, has_flag, key, xbytes) in enumerate(xor_hits, 1):
                desc = f'XOR key=0x{key:02x} ratio={ratio:.2f} flag={has_flag}'
                step += 1
                save_layer(step, xbytes, f'layer2 cand {idx} xor{rank}: {desc}')
                # Attempt downstream decodings on XORed bytes
                cur = xbytes
                ok, nxt = try_hex_decode(cur)
                if ok:
                    step += 1
                    save_layer(step, nxt, f'hex decoded after XOR key=0x{key:02x}')
                    cur = nxt
                ok, nxt = try_base64_decode(cur)
                if ok:
                    step += 1
                    save_layer(step, nxt, f'base64 decoded after XOR key=0x{key:02x}')
                    cur = nxt
                ok, nxt, label = try_decompress(cur)
                if ok:
                    step += 1
                    save_layer(step, nxt, f'decompressed ({label}) after XOR key=0x{key:02x}')
                    cur = nxt
                if looks_printable(cur):
                    try:
                        print('\n----- XOR Candidate Text -----\n')
                        print(cur.decode('utf-8', errors='replace'))
                        print('\n--------------------------------\n')
                    except Exception:
                        pass

            # Try automatic next decodes (without XOR) as before
            ok, nxt = try_hex_decode(data)
            if ok:
                step += 1
                save_layer(step, nxt, 'hex decoded from layer2 candidate')
                data = nxt
            ok, nxt = try_base64_decode(data)
            if ok:
                step += 1
                save_layer(step, nxt, 'base64 decoded from layer2 candidate')
                data = nxt
            ok, nxt, label = try_decompress(data)
            if ok:
                step += 1
                save_layer(step, nxt, f'decompressed ({label}) from layer2 candidate')
                data = nxt
            if looks_printable(data):
                try:
                    print('\n----- Candidate Text -----\n')
                    print(data.decode('utf-8', errors='replace'))
                    print('\n-------------------------\n')
                except Exception:
                    pass
        return

    # Heuristic decoding loop for up to a few steps (fallback)
    for _ in range(6):
        progressed = False

        # If it looks like hex text
        if not progressed and re.fullmatch(b'[0-9A-Fa-f\s]+', current or b'') and len(current) > 0:
            ok, nxt = try_hex_decode(current)
            if ok:
                current = nxt
                save_layer(step, current, 'hex decoded')
                step += 1
                progressed = True
                continue

        # Try base64
        if not progressed:
            ok, nxt = try_base64_decode(current)
            if ok:
                current = nxt
                save_layer(step, current, 'base64 decoded')
                step += 1
                progressed = True
                continue

        # Try zlib/gzip/deflate
        if not progressed:
            ok, nxt, label = try_decompress(current)
            if ok:
                current = nxt
                save_layer(step, current, f'decompressed ({label})')
                step += 1
                progressed = True
                continue

        # If looks printable, stop
        if looks_printable(current):
            save_layer(step, current, 'printable text')
            try:
                print('\n----- Decoded Text -----\n')
                print(current.decode('utf-8'))
                print('\n------------------------\n')
            except Exception:
                pass
            break

        # No progress; stop
        break

    # Final hints
    if current.startswith(b'PK\x03\x04'):
        print('[!] Output is a ZIP. Extract manually if needed.')
    elif current.startswith(b'\x89PNG'):
        print('[!] Output is a PNG image.')
    elif current.startswith(b'%PDF'):
        print('[!] Output is a PDF document.')


if __name__ == '__main__':
    main()
