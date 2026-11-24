#!/usr/bin/env python3
import zlib, struct, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "brand")
os.makedirs(OUT, exist_ok=True)

BG   = (0x0C, 0x2C, 0x52)
ACC  = (0xF2, 0x9F, 0x05)
WHT  = (0xE8, 0xEF, 0xF7)

def make_png(size, pixels):
    def chunk(typ, data):
        return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
    raw = b""
    for row in pixels:
        raw += b"\x00" + row
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")

def build_icon(size):
    canvas = [BG] * (size * size)  # Lista plana de 3 bytes por píxel
    def setpx(x, y, color):
        if 0 <= x < size and 0 <= y < size:
            canvas[y*size + x] = color
    cx = cy = size // 2
    r = int(size*0.30); w = max(4, int(size*0.055))
    for y in range(size):
        for x in range(size):
            d2 = (x-cx)**2 + (y-cy)**2
            if (r-w)**2 <= d2 <= r*r:
                setpx(x, y, ACC)
    thick = max(4, int(size*0.07))
    pts = [(cx-70, cy-10), (cx-20, cy+55), (cx+80, cy-55)]
    for i in range(len(pts)-1):
        x0, y0 = pts[i]; x1, y1 = pts[i+1]
        steps = 120
        for t in range(steps+1):
            x = int(x0 + (x1-x0)*t/steps); y = int(y0 + (y1-y0)*t/steps)
            for dx in range(-thick//2, thick//2+1):
                for dy in range(-thick//2, thick//2+1):
                    setpx(x+dx, y+dy, WHT)
    FONT = {
        'A':["  #  "," # # "," # # ","#####"," # # "," # # "," # # "],
        'D':["#### ","#   #","#   #","#   #","#   #","#   #","#### "],
        'U':[" # # "," # # "," # # "," # # "," # # "," # # "," ###  "],
        ' ':["     ","     ","     ","     ","     ","     ","     "],
    }
    text = "ADU"
    total_w = sum(len(FONT[c][0]) for c in text) + 5*(len(text)-1)
    x = cx - total_w//2
    y0 = int(size*0.70)
    ts = max(4, int(size*0.05))
    for ch in text:
        glyph = FONT[ch]
        gw = len(glyph[0])
        for row in range(7):
            for col in range(gw):
                if glyph[row][col] == '#':
                    px = x + col
                    py = y0 + row*ts
                    for sy in range(ts):
                        for sx in range(ts):
                            setpx(px+sx, py+sy, WHT)
        x += gw + 5
    pixels = []
    for y in range(size):
        row = b""
        for x in range(size):
            r, g, b = canvas[y*size + x]
            row += bytes([r, g, b])
        pixels.append(row)
    return pixels

for s, name in ((192, "logo192.png"), (512, "logo512.png"), (180, "apple-touch-icon.png")):
    png = make_png(s, build_icon(s))
    path = os.path.join(OUT, name)
    with open(path, "wb") as f:
        f.write(png)
    print("ok", name, s, "x", s, len(png), "bytes")