#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont, ImageChops
import string
import numpy as np


CHAR_WIDTH = 35
CHAR_HEIGHT = 81
RECT_TOP = 15
RECT_BOTTOM = CHAR_HEIGHT - 23  # 58 per chall.py


def load_font(font_path: str) -> ImageFont.ImageFont:
    return ImageFont.load(font_path)


def render_masked_char(character: str, font: ImageFont.ImageFont) -> Image:
    canvas = Image.new("RGB", (CHAR_WIDTH, CHAR_HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((0, 0), character, font=font, fill=(0, 0, 0), anchor="lt", align="left")
    draw.rectangle([(0, RECT_TOP), (CHAR_WIDTH, RECT_BOTTOM)], fill="blue")
    return canvas


def image_abs_difference_sum(a: Image, b: Image) -> int:
    if a.mode != "RGB":
        a = a.convert("RGB")
    if b.mode != "RGB":
        b = b.convert("RGB")
    # Use numpy for a fast absolute-difference sum
    arr_a = np.asarray(a, dtype=np.int16)
    arr_b = np.asarray(b, dtype=np.int16)
    return int(np.abs(arr_a - arr_b).sum())


def build_candidate_set() -> str:
    # Exclude characters explicitly ruled out by chall.py
    excluded = set("*+-:=~")
    # Likely flag alphabet for CTFs
    likely = string.ascii_letters + string.digits + "{}_!@#$%^&()[];',.<>/?\\|`\" "
    # Remove excluded
    return "".join(ch for ch in likely if ch not in excluded)


def solve(output_path: str, font_path: str) -> str:
    output_image = Image.open(output_path).convert("RGB")
    width, height = output_image.size
    assert height == CHAR_HEIGHT, f"Unexpected output height: {height} != {CHAR_HEIGHT}"
    assert width % CHAR_WIDTH == 0, "Output width is not a multiple of char width"

    num_chars = width // CHAR_WIDTH
    candidates = build_candidate_set()
    font = load_font(font_path)

    # Pre-render all masked candidate glyphs once
    rendered_cache = {c: render_masked_char(c, font) for c in candidates}

    recovered_chars = []
    for index in range(num_chars):
        x0 = index * CHAR_WIDTH
        x1 = x0 + CHAR_WIDTH
        cell = output_image.crop((x0, 0, x1, CHAR_HEIGHT))

        best_char = None
        best_score = None
        for c, glyph_img in rendered_cache.items():
            score = image_abs_difference_sum(cell, glyph_img)
            if best_score is None or score < best_score:
                best_score = score
                best_char = c

        recovered_chars.append(best_char if best_char is not None else "?")

    return "".join(recovered_chars)


if __name__ == "__main__":
    output_png = "output.png"
    font_file = "ComicMono.pil"  # Provided alongside .pbm
    flag = solve(output_png, font_file)
    print(flag)


