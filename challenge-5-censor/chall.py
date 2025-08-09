#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from secret import flag

char_width = 35
char_height = 81
font_path = "./font/ComicMono.pil"
font = ImageFont.load(font_path)

small_punctuation = "*+-:=~"
assert all(c not in small_punctuation for c in flag)

img = Image.new("RGB", (len(flag) * char_width, char_height), (255, 255, 255))
draw = ImageDraw.Draw(img)

draw.text((0, 0), flag, font=font, fill=(0, 0, 0), anchor="lt", align="left")
draw.rectangle([(0, 15), (len(flag) * char_width, char_height - 23)], fill="blue")

img.save("output.png")
