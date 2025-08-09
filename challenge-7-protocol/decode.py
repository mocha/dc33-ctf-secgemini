#!/usr/bin/env python3
"""
Blind BFSK decoder for the provided audio. We assume two tones near 270 Hz and 540 Hz
and sweep a reasonable range of bit rates. For each candidate, we compute short-time
Goertzel power at both tones and sample at the symbol period to decide bits. Then we
pack bits into bytes (LSB-first) and print ASCII if it seems printable.
"""
from __future__ import annotations

import sys
import math
from typing import Iterable, Tuple
import numpy as np
import soundfile as sf


def load_audio_mono(path: str) -> Tuple[np.ndarray, int]:
    y, sr = sf.read(path, always_2d=False)
    if y.ndim == 2:
        y = y.mean(axis=1)
    return y.astype(np.float32), sr


def st_power(signal: np.ndarray, sr: int, freq: float, win: int) -> np.ndarray:
    """Short-time quadrature energy at a given frequency using a moving window.
    Phase-invariant by summing in-phase and quadrature components.
    """
    t = np.arange(len(signal), dtype=np.float32) / sr
    s = np.sin(2 * np.pi * freq * t)
    c = np.cos(2 * np.pi * freq * t)
    i = signal * c
    q = signal * s
    kernel = np.ones(win, dtype=np.float32)
    Ii = np.convolve(i, kernel, mode="same")
    Qq = np.convolve(q, kernel, mode="same")
    return Ii * Ii + Qq * Qq


def bits_from_bfsk(y: np.ndarray, sr: int, f0: float, f1: float, baud: float) -> np.ndarray:
    samples_per_bit = int(round(sr / baud))
    if samples_per_bit < 8:
        raise ValueError("samples_per_bit too small")
    # Smooth power envelopes with a moderate window
    win = max(16, samples_per_bit // 3)
    p0 = st_power(y, sr, f0, win)
    p1 = st_power(y, sr, f1, win)
    diff = p1 - p0

    # Choose offset that maximizes absolute symbol means over initial region
    best_offset = 0
    best_metric = -1.0
    for offset in range(0, samples_per_bit):
        # Average within each symbol window directly
        vals = []
        ptr = offset
        for _ in range(1000):  # inspect first ~1000 symbols
            end = ptr + samples_per_bit
            if end >= len(diff):
                break
            vals.append(diff[ptr:end].mean())
            ptr = end
        if not vals:
            break
        metric = abs(np.mean(vals))
        if metric > best_metric:
            best_metric = metric
            best_offset = offset

    # Now generate bits over entire signal using the chosen offset
    bits = []
    ptr = best_offset
    while ptr + samples_per_bit <= len(diff):
        seg = diff[ptr:ptr + samples_per_bit]
        bits.append(1 if seg.mean() > 0 else 0)
        ptr += samples_per_bit
    return np.array(bits, dtype=np.uint8)


def bytes_from_bits(bits: np.ndarray) -> bytes:
    # Assume 8-N-1 framing or raw 8-bit? Try raw 8-bit first.
    # Pack every 8 bits MSB-first.
    n = (len(bits) // 8) * 8
    bits = bits[:n].reshape(-1, 8)
    vals = (bits * (1 << (7 - np.arange(8)))).sum(axis=1)
    return bytes(int(v) for v in vals)


def bytes_from_bits_lsb(bits: np.ndarray) -> bytes:
    n = (len(bits) // 8) * 8
    bits = bits[:n].reshape(-1, 8)
    weights = 1 << np.arange(8)
    vals = (bits * weights).sum(axis=1)
    return bytes(int(v) for v in vals)


def uart8n1_from_bits(bits: np.ndarray) -> bytes:
    out = []
    i = 0
    while i + 10 <= len(bits):
        if bits[i] == 0 and bits[i + 9] == 1:
            # LSB-first data
            data_bits = bits[i + 1:i + 9]
            val = int((data_bits * (1 << np.arange(8))).sum())
            out.append(val)
            i += 10
        else:
            i += 1
    return bytes(out)


def try_decode(path: str) -> None:
    y, sr = load_audio_mono(path)
    f0, f1 = 270.0, 540.0
    for baud in [20, 25, 30, 35, 40, 45, 50, 60, 75, 90, 100, 120, 150, 180, 200, 240, 300, 360, 400]:
        try:
            bits = bits_from_bfsk(y, sr, f0, f1, baud)
        except Exception as e:
            continue
        decoders = [
            ("raw_msb", bytes_from_bits(bits)),
            ("raw_lsb", bytes_from_bits_lsb(bits)),
            ("uart8n1", uart8n1_from_bits(bits)),
        ]
        for label, data in decoders:
            text = data.decode('utf-8', errors='ignore')
            if any(word in text for word in ["CREATE", "TABLE", "INSERT", "name", "column"]):
                print(f"--- baud {baud} {label} hit; length {len(data)} ---")
                print(text[:2000])


if __name__ == "__main__":
    try_decode(sys.argv[1] if len(sys.argv) > 1 else 'protocol.mp3')


