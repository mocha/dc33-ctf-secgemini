#!/usr/bin/env python3
import numpy as np
import soundfile as sf


def load(path: str):
    y, sr = sf.read(path, always_2d=False)
    if y.ndim == 2:
        y = y.mean(axis=1)
    y = y.astype(np.float32)
    return y, sr


def tone_bank(sr: int):
    # Candidate tones observed ~ 153..270 step 6 Hz
    tones = np.arange(153.0, 271.0 + 1e-6, 6.0)
    return tones


def detect(y: np.ndarray, sr: int, hop_ms: float = 40.0, win_ms: float = 40.0):
    hop = int(sr * hop_ms / 1000.0)
    win = int(sr * win_ms / 1000.0)
    half = win // 2
    tones = tone_bank(sr)
    t = np.arange(win, dtype=np.float32) / sr
    # Precompute sin/cos kernels for each tone
    kernels = []
    for f in tones:
        c = np.cos(2 * np.pi * f * t).astype(np.float32)
        s = np.sin(2 * np.pi * f * t).astype(np.float32)
        kernels.append((c, s))
    indices = []
    freqs = []
    for start in range(0, len(y) - win, hop):
        seg = y[start:start + win]
        powers = []
        for c, s in kernels:
            i = np.dot(seg, c)
            q = np.dot(seg, s)
            powers.append(i * i + q * q)
        idx = int(np.argmax(powers))
        indices.append(idx)
        freqs.append(tones[idx])
    return np.array(indices), np.array(freqs)


def try_map(indices: np.ndarray):
    # Heuristic: collapse repeats into runs (symbol per change)
    runs = [indices[0]]
    for v in indices[1:]:
        if v != runs[-1]:
            runs.append(v)
    arr = np.array(runs, dtype=np.int32)
    # Try base-16 mapping from lowest 16 symbols
    out = ''.join('0123456789abcdef'[v % 16] for v in arr[:400])
    print('First 400 mapped to hex:', out)


if __name__ == '__main__':
    y, sr = load('protocol.mp3')
    idx, freqs = detect(y, sr)
    unique = np.unique(idx)
    print('unique levels:', len(unique))
    print('freq range:', freqs.min(), freqs.max())
    try_map(idx)


