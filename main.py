"""Draw one image summing up the world news of Thursday 19 November 2026.

Pure Python 3 standard library, no network, no files read: the picture is
drawn from the six stories in STORIES below, so two runs write exactly the
same bytes. Run: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (28, 28, 28)
NAVY = (20, 33, 61)
GOLD = (201, 162, 39)
SNOW = (255, 255, 255)
MUTE = (96, 96, 96)
LINE = (214, 214, 214)

STORIES = [
    ("ANTHROPIC IPO", (96, 48, 148),
     "Biggest IPO ever: $81.3bn. ANT shares "
     "start trading on Nasdaq today."),
    ("SHENZHEN SUMMIT", NAVY,
     "Xi, Putin and Trump meet in Shenzhen "
     "for a rare three-way summit."),
    ("WORLD COURT", (0, 120, 120),
     "The ICJ rules today on Myanmar's "
     "Rohingya case, brought by Gambia."),
    ("GTA VI LAUNCH", (178, 34, 34),
     "GTA VI rolls out worldwide. Gamers "
     "return to Vice City after 13 years."),
    ("HORMUZ TANKERS", (150, 84, 0),
     "Three tankers catch fire after "
     "hitting mines near the Strait of Hormuz."),
    ("GAZA GROUND OP", (120, 20, 60),
     "Israeli troops enter central Gaza. "
     "Allies urge aid access as floods hit."),
]

# 5x7 bitmap font. Each glyph is seven strings of five "#" / "." cells.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}


class Picture:
    """An RGB pixel buffer with filled shapes and bitmap text."""

    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.buf = bytearray(colour * (width * height))

    def px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            row = (yy * self.w + x) * 3
            self.buf[row:row + w * 3] = bytes(colour) * w

    def ring(self, cx, cy, r, colour, thick=3):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= thick / 2:
                    self.px(xx, yy, colour)

    def glyph(self, x, y, ch, scale, colour):
        rows = GLYPHS.get(ch, GLYPHS[" "])
        for r, line in enumerate(rows):
            for c, cell in enumerate(line):
                if cell == "1":
                    self.rect(x + c * scale, y + r * scale,
                              scale, scale, colour)

    def text(self, x, y, s, scale, colour):
        cx = x
        for ch in s.upper():
            self.glyph(cx, y, ch, scale, colour)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def centred(self, cx, y, s, scale, colour):
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, colour)

    @staticmethod
    def split_lines(s, max_chars):
        out = []
        cur = ""
        for word in s.split(" "):
            trial = (cur + " " + word).strip()
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    out.append(cur)
                cur = word
        if cur:
            out.append(cur)
        return out


def card(pic, title, colour, body, x, y, w, h):
    pic.rect(x, y, w, h, SNOW)
    pic.rect(x, y, w, 10, colour)
    pic.rect(x + 24, y + 28, 14, 14, colour)
    pic.text(x + 46, y + 22, title, 5, colour)
    yy = y + 88
    for line in pic.split_lines(body, 20)[:4]:
        pic.text(x + 24, yy, line, 4, INK)
        yy += 38
    pic.rect(x, y + h - 2, w, 2, LINE)


def header_rule(pic, y, colour):
    pic.rect(W // 2 - 140, y, 280, 2, colour)
    pic.rect(W // 2 - 140, y - 6, 2, 10, colour)
    pic.rect(W // 2 + 138, y - 6, 2, 10, colour)


def encode_png(pic):
    raw = bytearray()
    for yy in range(pic.h):
        raw.append(0)
        start = yy * pic.w * 3
        raw += pic.buf[start:start + pic.w * 3]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    head = struct.pack(">IIBBBBB", pic.w, pic.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", head)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    pic = Picture(W, H, PAPER)
    pic.rect(0, 0, W, 150, NAVY)
    pic.ring(66, 75, 34, GOLD, 4)
    pic.rect(32, 75, 68, 4, GOLD)
    pic.rect(66, 41, 4, 68, GOLD)
    pic.centred(W // 2, 22, "WORLD NEWS", 8, SNOW)
    pic.centred(W // 2, 100, "THURSDAY 19 NOVEMBER 2026", 5, GOLD)
    pic.rect(0, 150, W, 6, GOLD)
    pic.centred(W // 2, 168, "SIX STORIES FROM ONE DAY", 4, MUTE)
    header_rule(pic, 199, GOLD)
    top = 204
    pw = 496
    ph = 240
    gap = 12
    for i, (title, colour, body) in enumerate(STORIES):
        px = 8 + (i % 2) * (pw + gap)
        py = top + (i // 2) * (ph + gap)
        card(pic, title, colour, body, px, py, pw, ph)
    pic.rect(0, 948, W, 76, NAVY)
    pic.centred(W // 2, 962, "19 NOV 2026 - THE DAY IN SIX PICTURES",
                4, SNOW)
    pic.centred(W // 2, 996,
                "SOURCES: AL JAZEERA - BLOOMBERG - THE HINDU - NDTV",
                3, GOLD)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(encode_png(pic))


if __name__ == "__main__":
    main()
