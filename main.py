#!/usr/bin/env python3
"""THE WORLD IN ONE PICTURE: Saturday 21 November 2026.

Draws a dense newspaper front page, 1024 by 1024 pixels, with the
Python standard library only. It sums up 42 stories that happened, or
were first reported, on Saturday 21 November 2026: three hero panels,
twelve illustrated leads, a sketch world map with numbered pins, and
twenty-seven one-line briefs, plus a by-the-numbers strip and a
date-check footer that names the big stories that are NOT today's
(the ICJ Myanmar ruling and the Shenzhen trilateral were both
19 November; the Anthropic debut was 19 November too).

The program is deterministic: no clock, no randomness, no network.
It writes entry.png to $MAKEFUN_OUTPUT_DIR when that is set, and to
/output/entry.png otherwise.

Run:  python3 main.py
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (179, 35, 27)
NAVY = (20, 38, 77)
TEAL = (14, 110, 110)
GOLD = (201, 141, 32)
SKY = (168, 208, 232)
SKYNIGHT = (16, 28, 58)
GREY = (110, 108, 100)
LIGHT = (238, 231, 214)
GREEN = (46, 110, 58)
PITCH = (58, 128, 66)
CREAM = (253, 246, 227)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (224, 110, 20)
DARKRED = (120, 22, 18)
STEEL = (150, 158, 165)
SAND = (226, 205, 158)
DUST = (196, 178, 140)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def frame(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d - r * r) <= r:
                        self.set(xx, yy, c)

    def disc(self, cx, cy, r, c):
        self.circle(cx, cy, r, c, fill=True)

    def ring(self, cx, cy, r, c):
        self.circle(cx, cy, r, c, fill=False)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        # filled triangle by scanline
        xs = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = xs
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / float(by - ay) if by != ay else 0.0
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / float(cy - by) if cy != by else 0.0
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / float(cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            self.hline(lo, y, hi - lo + 1, c)

    def poly(self, pts, c):
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            self.line(x0, y0, x1, y1, c)


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 bits. Lowercase maps to uppercase, so
# headlines stay in one clean case and M and W keep their shapes.
_G = {}


def _g(ch, rows):
    _G[ch] = tuple(int(r.replace("#", "1").replace(".", "0"), 2)
                   for r in rows)


_g("A", ("01110", "10001", "10001", "11111", "10001", "10001", "10001"))
_g("B", ("11110", "10001", "10001", "11110", "10001", "10001", "11110"))
_g("C", ("01110", "10001", "10000", "10000", "10000", "10001", "01110"))
_g("D", ("11110", "10001", "10001", "10001", "10001", "10001", "11110"))
_g("E", ("11111", "10000", "10000", "11110", "10000", "10000", "11111"))
_g("F", ("11111", "10000", "10000", "11110", "10000", "10000", "10000"))
_g("G", ("01110", "10001", "10000", "10111", "10001", "10001", "01111"))
_g("H", ("10001", "10001", "10001", "11111", "10001", "10001", "10001"))
_g("I", ("01110", "00100", "00100", "00100", "00100", "00100", "01110"))
_g("J", ("00111", "00010", "00010", "00010", "00010", "10010", "01100"))
_g("K", ("10001", "10010", "10100", "11000", "10100", "10010", "10001"))
_g("L", ("10000", "10000", "10000", "10000", "10000", "10000", "11111"))
_g("M", ("10001", "11011", "10101", "10101", "10001", "10001", "10001"))
_g("N", ("10001", "11001", "10101", "10011", "10001", "10001", "10001"))
_g("O", ("01110", "10001", "10001", "10001", "10001", "10001", "01110"))
_g("P", ("11110", "10001", "10001", "11110", "10000", "10000", "10000"))
_g("Q", ("01110", "10001", "10001", "10001", "10101", "10010", "01101"))
_g("R", ("11110", "10001", "10001", "11110", "10100", "10010", "10001"))
_g("S", ("01111", "10000", "10000", "01110", "00001", "00001", "11110"))
_g("T", ("11111", "00100", "00100", "00100", "00100", "00100", "00100"))
_g("U", ("10001", "10001", "10001", "10001", "10001", "10001", "01110"))
_g("V", ("10001", "10001", "10001", "10001", "10001", "01010", "00100"))
_g("W", ("10001", "10001", "10001", "10101", "10101", "11011", "10001"))
_g("X", ("10001", "10001", "01010", "00100", "01010", "10001", "10001"))
_g("Y", ("10001", "10001", "01010", "00100", "00100", "00100", "00100"))
_g("Z", ("11111", "00001", "00010", "00100", "01000", "10000", "11111"))
_g("0", ("01110", "10001", "10011", "10101", "11001", "10001", "01110"))
_g("1", ("00100", "01100", "00100", "00100", "00100", "00100", "01110"))
_g("2", ("01110", "10001", "00001", "00110", "01000", "10000", "11111"))
_g("3", ("11111", "00010", "00100", "00010", "00001", "10001", "01110"))
_g("4", ("00010", "00110", "01010", "10010", "11111", "00010", "00010"))
_g("5", ("11111", "10000", "11110", "00001", "00001", "10001", "01110"))
_g("6", ("01110", "10000", "10000", "11110", "10001", "10001", "01110"))
_g("7", ("11111", "00001", "00010", "00100", "01000", "01000", "01000"))
_g("8", ("01110", "10001", "10001", "01110", "10001", "10001", "01110"))
_g("9", ("01110", "10001", "10001", "01111", "00001", "00001", "01110"))
_g(" ", ("00000", "00000", "00000", "00000", "00000", "00000", "00000"))
_g(".", ("00000", "00000", "00000", "00000", "00000", "01100", "01100"))
_g(",", ("00000", "00000", "00000", "00000", "01100", "00100", "01000"))
_g(":", ("00000", "01100", "01100", "00000", "01100", "01100", "00000"))
_g(";", ("00000", "01100", "01100", "00000", "01100", "00100", "01000"))
_g("'", ("00100", "00100", "01000", "00000", "00000", "00000", "00000"))
_g("-", ("00000", "00000", "00000", "01110", "00000", "00000", "00000"))
_g("!", ("00100", "00100", "00100", "00100", "00100", "00000", "00100"))
_g("?", ("01110", "10001", "00001", "00110", "00100", "00000", "00100"))
_g("%", ("11001", "11010", "00010", "00100", "01000", "01011", "10011"))
_g("(", ("00010", "00100", "01000", "01000", "01000", "00100", "00010"))
_g(")", ("01000", "00100", "00010", "00010", "00010", "00100", "01000"))
_g("/", ("00001", "00010", "00010", "00100", "01000", "01000", "10000"))
_g("&", ("01100", "10010", "10100", "01000", "10101", "10010", "01101"))
_g("+", ("00000", "00100", "00100", "01110", "00100", "00100", "00000"))
_g("=", ("00000", "00000", "11111", "00000", "11111", "00000", "00000"))
_g("$", ("00100", "01111", "10100", "01110", "00101", "11110", "00100"))
_g("*", ("00000", "10101", "01110", "11111", "01110", "10101", "00000"))
_g("#", ("01010", "01010", "11111", "01010", "11111", "01010", "01010"))
_g("<", ("00010", "00100", "01000", "10000", "01000", "00100", "00010"))
_g(">", ("01000", "00100", "00010", "00001", "00010", "00100", "01000"))
_g("@", ("01110", "10001", "10111", "10101", "10110", "10000", "01110"))
_g("_", ("00000", "00000", "00000", "00000", "00000", "00000", "11111"))


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = _G.get(ch, _G["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.rect(cx + col * scale, y + row * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx


def wrap(s, scale, max_w):
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(cv, x, y, lines, scale, color, lh=None):
    if lh is None:
        lh = 9 * scale
    for ln in lines:
        draw_text(cv, x, y, ln, scale, color)
        y += lh
    return y

# ---------------------------------------------------------------- stories
# Every story happened, or was first reported, on Saturday 21 Nov 2026.
# Region codes: EU Europe, NA North America, ME Middle East, AS Asia,
# AF Africa, OC Oceania, WO World. Field codes: WAR war and diplomacy,
# MKT markets and business, SPT sport, TEC tech and science, SOC
# society and justice, CLI climate and energy.
HEROES = [
    ("MISSILES OVER",
     "KYIV AND POLAND",
     ["400 DRONES, 110 MISSILES", "9 DEAD, 2 FALL IN POLAND"],
     "EU", "WAR"),
    ("WALL STREET'S",
     "FRIDAY ROUT",
     ["NASDAQ -5.3% IN A DAY", "NVIDIA -14% IN ONE DAY"],
     "NA", "MKT"),
    ("RAHUL 93 NOT OUT",
     "INDIA FIGHT BACK",
     ["INDIA 239-1 AT LUNCH", "NEW ZEALAND MADE 368"],
     "OC", "SPT"),
]

LEADS = [
    ("VEGAS UNDER LIGHTS", "Qualifying runs at dawn UTC and the race "
     "is Saturday night on the Strip. Champion Antonelli leads the "
     "field into the final triple-header.", "F1", "NA", "SPT"),
    ("VOYAGER 1 A LIGHT-DAY OUT", "49 years after launch, NASA's "
     "probe is the first human-made object a light-day from Earth.",
     "SPACE", "WO", "TEC"),
    ("GAZA'S CHILDREN: 22,000 DEAD", "The health ministry says more "
     "than 22,000 children have now been killed in Gaza.", "GAZA",
     "ME", "WAR"),
    ("EBOLA SHUTS 100 SCHOOLS", "Children are hit hardest as the "
     "outbreak spreads in eastern Congo.", "EBOLA", "AF", "SOC"),
    ("EU: DON'T LET COP31 GO FOSSIL", "Brussels warns the climate "
     "summit must not turn into a fossil-fuel summit.", "CLIMATE",
     "WO", "CLI"),
    ("BUKELE SEEKS THIRD TERM", "El Salvador's president moves to "
     "stay in power until 2033.", "VOTE", "NA", "SOC"),
    ("HOUTHI MISSILE HITS RIYADH TOWER", "A tower in the King "
     "Abdullah Financial District is struck. No injuries are "
     "reported.", "RIYADH", "ME", "WAR"),
    ("ESTONIA TO SHUT RUSSIA BORDER", "Road crossings close from "
     "1 December over sustained aggression, Tallinn says.", "BORDER",
     "EU", "WAR"),
    ("BRADY EYES CHELSEA STAKE", "Tom Brady is in talks to buy a "
     "minority stake in Chelsea FC.", "FOOTBALL", "EU", "SPT"),
    ("INDIA'S BOYS REACH ASIAN CUP", "A 0-0 draw with Malaysia "
     "seals U17 Asian Cup qualification for India.", "FOOTBALL",
     "AS", "SPT"),
    ("TRUMP FIRES CYBER CHIEF", "The director of national "
     "cybersecurity is sacked by the president.", "CYBER", "NA",
     "TEC"),
    ("CALIFORNIA SUBPOENAS NVIDIA", "The state demands answers over "
     "alleged chip sales to China.", "CHIPS", "NA", "TEC"),
]

BRIEFS = [
    ("EU gives Ukraine 1bn euros in arms aid", "EU", "WAR"),
    ("Europe calls for winter ceasefire", "EU", "WAR"),
    ("NATO chief to visit Warsaw on Saturday", "EU", "WAR"),
    ("US team seeks Ukraine deal by end of Jan", "NA", "WAR"),
    ("US, Israel weigh new strike on Tehran", "ME", "WAR"),
    ("US-Iran tit-for-tat strikes go on", "ME", "WAR"),
    ("US presses Singapore on Iran sanctions", "AS", "WAR"),
    ("UK reports sea incident off Mukalla", "ME", "WAR"),
    ("Two Salvadorans killed in Haiti blast", "NA", "SOC"),
    ("US jails Gupta 19 years over Pannun plot", "NA", "SOC"),
    ("Morocco pledges 366m euros for arms", "AF", "WAR"),
    ("US opens Pacific to deep-sea mining", "NA", "CLI"),
    ("Taiwan flags China-linked Meta accounts", "AS", "TEC"),
    ("Trump backs second chance for Huang", "NA", "MKT"),
    ("Anthropic falls 9% in second day of trade", "NA", "MKT"),
    ("AMD -12% as chip rout deepens", "NA", "MKT"),
    ("VIX jumps 33% to 37 as fear spikes", "NA", "MKT"),
    ("Hazlewood warns over Cummins captaincy", "OC", "SPT"),
    ("Australia v England T20I in Melbourne", "OC", "SPT"),
    ("East Bengal and SC Delhi draw 2-2", "AS", "SPT"),
    ("Bengaluru go top of the ISL after 2-0 win", "AS", "SPT"),
    ("UN: 357,000 displaced in Yemen since Aug", "ME", "SOC"),
    ("Rohingya welcome landmark court verdict", "AS", "SOC"),
    ("China seeks full Rohingya resolution", "AS", "SOC"),
    ("Switzerland backs ICJ genocide ruling", "EU", "SOC"),
    ("Czechia weighs faster air-defence build", "EU", "WAR"),
    ("Iraq troops to deploy in Hezbollah area", "ME", "WAR"),
]

NUMBERS = [
    ("NASDAQ", "-5.3%", "Friday rout"),
    ("NVIDIA", "-14%", "in one day"),
    ("MISSILES", "110", "fired at Ukraine"),
    ("DEAD IN KYIV", "9", "in the barrage"),
    ("EU ARMS AID", "1bn EUR", "for Ukraine"),
    ("CHILDREN DEAD", "22,000", "in Gaza, ministry"),
]

REGIONS = [("EUROPE", "EU"), ("N. AMERICA", "NA"), ("MIDDLE EAST", "ME"),
           ("ASIA", "AS"), ("AFRICA", "AF"), ("OCEANIA", "OC"),
           ("WORLD", "WO")]
FIELDS = [("WAR + DIPLOMACY", "WAR"), ("MARKETS", "MKT"), ("SPORT", "SPT"),
          ("TECH + SCIENCE", "TEC"), ("SOCIETY", "SOC"),
          ("CLIMATE + ENERGY", "CLI")]

MAP_PINS = [
    (1, "KYIV", 0.585, 0.19),
    (2, "WARSAW", 0.558, 0.17),
    (3, "WELLINGTON", 0.93, 0.88),
    (4, "LAS VEGAS", 0.181, 0.29),
    (5, "GAZA", 0.596, 0.32),
    (6, "CONGO", 0.542, 0.59),
    (7, "RIYADH", 0.630, 0.38),
    (8, "TALLINN", 0.569, 0.12),
]

# Coarse dotted world map, 48 columns by 24 rows, drawn from a rough
# outline. Each row is a string; '#' is land, '.' is sea.
MAP_ROWS = [
    "...########.............######################..",
    "..###########..........#######################..",
    "..############.........#######################..",
    "...###########........#######################...",
    "...###########........#####################.....",
    "....#########.........####################......",
    "....########..........#######.....##########....",
    "....########..........###########..########.....",
    ".....#####............########...####.####......",
    "......####.............########..###.####.......",
    "........###............#########.###.####.......",
    ".........###...........#########....#####.......",
    "..........####.........########......######.....",
    "..........#####.........######........######....",
    "..........#####.........#####.........######....",
    "..........#####.........#####...........####....",
    "..........#####.........#####..........######...",
    "...........####..........####..........######...",
    "...........####..........###............####....",
    "...........###...........###............####....",
    "...........###...........##.............##......",
    "...........##...............................##..",
    "...........##...................................",
    "................................................",
]

# ---------------------------------------------------------------- scenes
def scene_kyiv(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKYNIGHT)
    for sx, sy in [(8, 8), (30, 20), (55, 6), (80, 16), (20, 34), (65, 30),
                   (90, 8), (42, 12), (72, 38), (15, 46), (95, 30)]:
        px = x + sx * w // 100
        py = y + sy * h // 100
        cv.disc(px, py, max(1, w // 200), WHITE)
    river_y = y + h * 62 // 100
    cv.rect(x, river_y, w, h - h * 62 // 100, (24, 68, 130))
    for bx in (12, 42, 72):
        bx0 = x + bx * w // 100
        bw = w * 22 // 100
        cv.hline(bx0, y + h * 55 // 100, bw, WHITE, 2)
        for k in range(5):
            px = bx0 + k * bw // 4
            cv.vline(px, y + h * 55 // 100, h * 12 // 100, WHITE, 2)
        cv.line(bx0, y + h * 55 // 100, bx0 + bw // 2,
                y + h * 44 // 100, WHITE)
        cv.line(bx0 + bw // 2, y + h * 44 // 100, bx0 + bw,
                y + h * 55 // 100, WHITE)
    for ex, ey, r in [(30, 26, 9), (62, 18, 12), (85, 34, 8)]:
        cx = x + ex * w // 100
        cy = y + ey * h // 100
        cv.disc(cx, cy, r * w // 200 + 3, ORANGE)
        cv.disc(cx, cy, r * w // 300 + 2, (255, 220, 90))
        for ang in range(0, 360, 45):
            import math as _m
            dx = int((r + 8) * w / 200 * _m.cos(_m.radians(ang)))
            dy = int((r + 8) * h / 200 * _m.sin(_m.radians(ang)))
            cv.line(cx, cy, cx + dx, cy + dy, (255, 220, 90))
    cv.line(x + w * 10 // 100, y + h * 8 // 100,
            x + w * 30 // 100, y + h * 26 // 100, WHITE)
    cv.line(x + w * 78 // 100, y + h * 6 // 100,
            x + w * 62 // 100, y + h * 18 // 100, WHITE)


def scene_chart(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    for gy in range(1, 4):
        cv.hline(x + 6, y + h * gy // 4, w - 12, LIGHT, 1)
    pts = [(4, 18), (22, 26), (38, 22), (55, 42), (70, 58), (86, 78),
           (96, 92)]
    for i in range(len(pts) - 1):
        x0 = x + pts[i][0] * w // 100
        y0 = y + pts[i][1] * h // 100
        x1 = x + pts[i + 1][0] * w // 100
        y1 = y + pts[i + 1][1] * h // 100
        cv.line(x0, y0, x1, y1, RED)
        cv.line(x0, y0 + 1, x1, y1 + 1, RED)
    ex = x + w * 96 // 100
    ey = y + h * 92 // 100
    cv.tri(ex - 12, ey - 14, ex + 2, ey - 2, ex - 2, ey - 16, RED)
    cv.disc(x + w * 38 // 100, y + h * 22 // 100, 3, GOLD)
    cv.disc(x + w * 70 // 100, y + h * 58 // 100, 3, GOLD)


def scene_cricket(cv, x, y, w, h):
    cv.rect(x, y, w, h, PITCH)
    cv.rect(x + w * 38 // 100, y + h * 12 // 100, w * 24 // 100,
            h * 76 // 100, (196, 164, 110))
    for k in range(3):
        sx = x + w * (44 + k * 4) // 100
        cv.vline(sx, y + h * 18 // 100, h * 16 // 100, (255, 230, 120), 3)
    cv.hline(x + w * 42 // 100, y + h * 16 // 100, w * 14 // 100,
             (255, 230, 120), 2)
    cv.rect(x + w * 58 // 100, y + h * 52 // 100, w * 5 // 100,
            h * 26 // 100, (150, 100, 50))
    cv.rect(x + w * 56 // 100, y + h * 44 // 100, w * 9 // 100,
            h * 10 // 100, (150, 100, 50))
    cv.disc(x + w * 74 // 100, y + h * 70 // 100, max(3, w // 28), RED)
    cv.disc(x + w * 72 // 100, y + h * 68 // 100, 2, WHITE)
    cv.hline(x + w * 8 // 100, y + h * 88 // 100, w * 84 // 100, WHITE, 2)


def scene_f1(cv, x, y, w, h):
    cv.rect(x, y, w, h, (12, 12, 28))
    for lx in range(0, 100, 8):
        cv.disc(x + lx * w // 100, y + h * 10 // 100, 2, GOLD)
    cv.rect(x, y + h * 62 // 100, w, h * 24 // 100, (60, 60, 70))
    cv.hline(x, y + h * 62 // 100, w, WHITE, 2)
    cv.hline(x, y + h * 86 // 100, w, WHITE, 2)
    cx = x + w * 50 // 100
    cy = y + h * 72 // 100
    cv.rect(cx - w * 26 // 100, cy - h * 8 // 100, w * 52 // 100,
            h * 14 // 100, RED)
    cv.rect(cx - w * 8 // 100, cy - h * 16 // 100, w * 18 // 100,
            h * 10 // 100, DARKRED)
    for wx in (-22, 20):
        cv.disc(cx + wx * w // 100, cy + h * 8 // 100, max(3, w // 30),
                BLACK)
        cv.ring(cx + wx * w // 100, cy + h * 8 // 100, max(3, w // 30),
                STEEL)
    cv.line(cx + w * 26 // 100, cy, x + w, y + h * 40 // 100, (255, 240, 160))
    cv.line(cx + w * 26 // 100, cy + 2, x + w, y + h * 44 // 100,
            (255, 240, 160))


def scene_space(cv, x, y, w, h):
    cv.rect(x, y, w, h, BLACK)
    for sx, sy in [(10, 12), (26, 30), (44, 8), (70, 18), (88, 10),
                   (58, 36), (20, 48), (80, 44), (36, 52), (94, 34)]:
        cv.disc(x + sx * w // 100, y + sy * h // 100, 2, WHITE)
    cx = x + w * 62 // 100
    cy = y + h * 46 // 100
    cv.line(x + w * 8 // 100, y + h * 88 // 100, cx, cy, STEEL)
    cv.line(x + w * 8 // 100, y + h * 88 // 100, cx - 8, cy + 6, STEEL)
    cv.rect(cx - 6, cy - 4, 26, 8, GOLD)
    cv.tri(cx + 20, cy - 12, cx + 20, cy + 12, cx + 38, cy, (255, 220, 120))
    cv.line(cx + 38, cy, x + w * 96 // 100, y + h * 12 // 100, GOLD)
    cv.disc(x + w * 92 // 100, y + h * 16 // 100, 4, (160, 200, 255))


def scene_gaza(cv, x, y, w, h):
    cv.rect(x, y, w, h, (232, 200, 150))
    cv.disc(x + w * 82 // 100, y + h * 18 // 100, max(4, w // 16),
            (255, 236, 180))
    for bx, bw, bh in [(6, 26, 62), (34, 22, 78), (58, 26, 54)]:
        bx0 = x + bx * w // 100
        by = y + h - h * bh // 100
        cv.rect(bx0, by, w * bw // 100, h * bh // 100, (120, 112, 100))
        cv.tri(bx0, by, bx0 + w * bw // 200, by - h * 10 // 100,
               bx0 + w * bw // 100, by, (120, 112, 100))
        for wy in range(by + h * 12 // 100, y + h - 4, h * 18 // 100):
            for wx in range(bx0 + 4, bx0 + w * bw // 100 - 6, w * 8 // 100):
                cv.rect(wx, wy, 3, 4, (70, 66, 58))
    for sx, sy, r in [(22, 30, 8), (48, 22, 10), (72, 30, 7)]:
        cv.disc(x + sx * w // 100, y + sy * h // 100, r, (200, 186, 158))
    cv.rect(x, y + h * 92 // 100, w, h * 8 // 100, (150, 138, 116))


def scene_ebola(cv, x, y, w, h):
    cv.rect(x, y, w, h, (240, 232, 214))
    cv.tri(x + w * 18 // 100, y + h * 78 // 100,
           x + w * 50 // 100, y + h * 22 // 100,
           x + w * 82 // 100, y + h * 78 // 100, WHITE)
    cv.frame(x + w * 18 // 100, y + h * 22 // 100, w * 64 // 100,
             h * 56 // 100, INK, 2)
    cv.rect(x + w * 45 // 100, y + h * 34 // 100, w * 10 // 100,
            h * 26 // 100, RED)
    cv.rect(x + w * 40 // 100, y + h * 42 // 100, w * 20 // 100,
            h * 10 // 100, RED)
    cv.rect(x + w * 44 // 100, y + h * 78 // 100, w * 12 // 100,
            h * 16 // 100, (90, 70, 50))
    cv.disc(x + w * 14 // 100, y + h * 82 // 100, 4, TEAL)
    cv.disc(x + w * 86 // 100, y + h * 82 // 100, 4, TEAL)


def scene_climate(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.disc(x + w * 84 // 100, y + h * 16 // 100, max(4, w // 18),
            (255, 214, 90))
    cx = x + w * 42 // 100
    cy = y + h * 52 // 100
    cv.disc(cx, cy, h * 34 // 100, (46, 130, 90))
    cv.rect(cx - h * 30 // 100, cy - h * 8 // 100, h * 22 // 100,
            h * 16 // 100, GREEN)
    cv.rect(cx + h * 2 // 100, cy + h * 4 // 100, h * 26 // 100,
            h * 12 // 100, (30, 90, 70))
    cv.rect(cx - h * 6 // 100, cy - h * 30 // 100, h * 10 // 100,
            h * 60 // 100, (30, 90, 70))
    for fx in (12, 78):
        fx0 = x + fx * w // 100
        cv.rect(fx0, y + h * 72 // 100, w * 8 // 100, h * 20 // 100, GREY)
        cv.rect(fx0 - 2, y + h * 64 // 100, w * 12 // 100, h * 8 // 100, GREY)
        cv.disc(fx0 + w * 4 // 100, y + h * 56 // 100, 5, (200, 200, 200))


def scene_vote(cv, x, y, w, h):
    cv.rect(x, y, w, h, (226, 232, 244))
    cv.rect(x + w * 28 // 100, y + h * 34 // 100, w * 44 // 100,
            h * 52 // 100, NAVY)
    cv.rect(x + w * 38 // 100, y + h * 30 // 100, w * 24 // 100,
            h * 6 // 100, BLACK)
    cv.rect(x + w * 44 // 100, y + h * 12 // 100, w * 18 // 100,
            h * 18 // 100, WHITE)
    cv.frame(x + w * 44 // 100, y + h * 12 // 100, w * 18 // 100,
             h * 18 // 100, INK, 1)
    cv.line(x + w * 46 // 100, y + h * 22 // 100,
            x + w * 50 // 100, y + h * 27 // 100, RED)
    cv.line(x + w * 50 // 100, y + h * 27 // 100,
            x + w * 60 // 100, y + h * 14 // 100, RED)
    for kx in range(0, 100, 12):
        cv.disc(x + kx * w // 100, y + h * 88 // 100, 2, GOLD)


def scene_riyadh(cv, x, y, w, h):
    cv.rect(x, y, w, h, (52, 44, 74))
    cv.disc(x + w * 80 // 100, y + h * 20 // 100, max(4, w // 18),
            (255, 226, 160))
    tx = x + w * 40 // 100
    cv.rect(tx, y + h * 22 // 100, w * 20 // 100, h * 70 // 100, (30, 30, 44))
    for wy in range(y + h * 28 // 100, y + h * 88 // 100, h * 10 // 100):
        for wx in range(tx + 4, tx + w * 20 // 100 - 4, w * 6 // 100):
            cv.rect(wx, wy, 3, 4, (255, 220, 120))
    for bx, bw, bh in [(8, 18, 48), (66, 20, 62), (88, 10, 40)]:
        cv.rect(x + bx * w // 100, y + h - h * bh // 100, w * bw // 100,
                h * bh // 100, (24, 24, 36))
    cx = tx + w * 10 // 100
    cy = y + h * 20 // 100
    cv.disc(cx, cy, 8, ORANGE)
    cv.disc(cx, cy, 4, (255, 220, 90))
    for ang in range(0, 360, 60):
        import math as _m
        dx = int(16 * _m.cos(_m.radians(ang)))
        dy = int(16 * _m.sin(_m.radians(ang)))
        cv.line(cx, cy, cx + dx, cy + dy, (255, 220, 90))
    cv.disc(cx - 14, cy - 10, 5, (160, 160, 170))
    cv.disc(cx + 12, cy - 16, 6, (160, 160, 170))


def scene_border(cv, x, y, w, h):
    cv.rect(x, y, w, h, (214, 226, 210))
    cv.rect(x, y + h * 58 // 100, w, h * 30 // 100, (120, 120, 118))
    cv.hline(x, y + h * 72 // 100, w, WHITE, 3)
    for i in range(8):
        col = RED if i % 2 == 0 else WHITE
        cv.rect(x + w * (8 + i * 11) // 100, y + h * 34 // 100,
                w * 11 // 100, h * 12 // 100, col)
    cv.vline(x + w * 8 // 100, y + h * 46 // 100, h * 12 // 100, INK, 3)
    cv.vline(x + w * 90 // 100, y + h * 46 // 100, h * 12 // 100, INK, 3)
    cv.rect(x + w * 62 // 100, y + h * 10 // 100, w * 26 // 100,
            h * 20 // 100, WHITE)
    cv.frame(x + w * 62 // 100, y + h * 10 // 100, w * 26 // 100,
             h * 20 // 100, RED, 2)
    cv.rect(x + w * 30 // 100, y + h * 78 // 100, w * 40 // 100,
            h * 12 // 100, (40, 90, 60))
    cv.rect(x + w * 34 // 100, y + h * 70 // 100, w * 32 // 100,
            h * 8 // 100, (40, 90, 60))


def scene_football(cv, x, y, w, h):
    cv.rect(x, y, w, h, PITCH)
    cv.hline(x + w * 6 // 100, y + h * 50 // 100, w * 88 // 100, WHITE, 2)
    cv.ring(x + w * 50 // 100, y + h * 50 // 100, h * 16 // 100, WHITE)
    cv.rect(x + w * 38 // 100, y + h * 6 // 100, w * 24 // 100,
            h * 10 // 100, WHITE)
    cv.frame(x + w * 38 // 100, y + h * 6 // 100, w * 24 // 100,
             h * 10 // 100, INK, 1)
    bx = x + w * 68 // 100
    by = y + h * 68 // 100
    cv.disc(bx, by, max(4, w // 14), WHITE)
    cv.disc(bx, by, 3, BLACK)
    for dx, dy in [(-6, -2), (6, -3), (0, 6), (-5, 4), (6, 3)]:
        cv.disc(bx + dx, by + dy, 2, BLACK)


def scene_cyber(cv, x, y, w, h):
    cv.rect(x, y, w, h, (18, 24, 40))
    cx = x + w * 50 // 100
    cy = y + h * 48 // 100
    pts = [(cx, cy - h * 34 // 100), (cx + w * 30 // 100, cy - h * 20 // 100),
           (cx + w * 30 // 100, cy + h * 6 // 100),
           (cx, cy + h * 34 // 100), (cx - w * 30 // 100, cy + h * 6 // 100),
           (cx - w * 30 // 100, cy - h * 20 // 100)]
    cv.poly(pts, TEAL)
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        cv.line(x0, y0, x1, y1, (90, 200, 190))
        cv.line(x0, y0 + 1, x1, y1 + 1, (90, 200, 190))
    cv.disc(cx, cy - h * 4 // 100, max(3, w // 24), GOLD)
    cv.rect(cx - 3, cy, 6, h * 14 // 100, GOLD)
    for sx in (14, 86):
        cv.disc(x + sx * w // 100, y + h * 16 // 100, 2, (90, 200, 190))


def scene_chips(cv, x, y, w, h):
    cv.rect(x, y, w, h, (16, 40, 32))
    cx = x + w * 50 // 100
    cy = y + h * 46 // 100
    s = min(w, h) * 44 // 100
    cv.rect(cx - s // 2, cy - s // 2, s, s, (20, 60, 50))
    cv.frame(cx - s // 2, cy - s // 2, s, s, (120, 200, 160), 2)
    cv.rect(cx - s // 4, cy - s // 4, s // 2, s // 2, (200, 170, 60))
    for k in range(-1, 2):
        cv.hline(cx - s // 2 - 6, cy + k * s // 4, 6, (120, 200, 160), 2)
        cv.hline(cx + s // 2, cy + k * s // 4, 6, (120, 200, 160), 2)
        cv.vline(cx + k * s // 4, cy - s // 2 - 6, 6, (120, 200, 160), 2)
        cv.vline(cx + k * s // 4, cy + s // 2, 6, (120, 200, 160), 2)
    ax = x + w * 82 // 100
    ay = y + h * 78 // 100
    cv.line(ax, ay - h * 30 // 100, ax, ay, RED)
    cv.line(ax, ay - h * 30 // 100, ax, ay, RED)
    cv.tri(ax - 8, ay - h * 30 // 100 + 12, ax + 8, ay - h * 30 // 100 + 12,
           ax, ay - h * 30 // 100 + 24, RED)
    cv.line(ax - 10, ay, ax + 10, ay, RED)


SCENES = {"KYIV": scene_kyiv, "CHART": scene_chart, "CRICKET": scene_cricket,
          "F1": scene_f1, "SPACE": scene_space, "GAZA": scene_gaza,
          "EBOLA": scene_ebola, "CLIMATE": scene_climate,
          "VOTE": scene_vote, "RIYADH": scene_riyadh,
          "BORDER": scene_border, "FOOTBALL": scene_football,
          "CYBER": scene_cyber, "CHIPS": scene_chips}
HERO_SCENES = ["KYIV", "CHART", "CRICKET"]

# ---------------------------------------------------------------- layout
def count_by(items, idx):
    out = {}
    for it in items:
        out[it[idx]] = out.get(it[idx], 0) + 1
    return out


def build():
    cv = Canvas(W, H, PAPER)
    all_stories = [(h[3], h[4]) for h in HEROES]
    all_stories += [(l[3], l[4]) for l in LEADS]
    all_stories += [(b[1], b[2]) for b in BRIEFS]
    n = len(all_stories)
    reg = count_by(all_stories, 0)
    fld = count_by(all_stories, 1)

    cv.frame(4, 4, W - 8, H - 8, INK, 2)

    # masthead
    title = "THE WORLD IN ONE PICTURE"
    draw_text(cv, (W - text_w(title, 5)) // 2, 14, title, 5, INK)
    date = "SATURDAY 21 NOVEMBER 2026"
    draw_text(cv, (W - text_w(date, 3)) // 2, 56, date, 3, RED)
    sub = "ONE DAY - ONE PAGE - %d STORIES" % n
    draw_text(cv, (W - text_w(sub, 2)) // 2, 84, sub, 2, INK)
    draw_text(cv, 14, 84, "NO. 325", 2, GREY)
    draw_text(cv, W - 14 - text_w("MAKE.FUN DAILY", 2), 84,
              "MAKE.FUN DAILY", 2, GREY)
    cv.hline(8, 100, W - 16, INK, 2)

    # numbers strip
    bw = 163
    for i, (label, value, note) in enumerate(NUMBERS):
        bx = 8 + i * (bw + 6)
        cv.frame(bx, 106, bw, 46, INK, 1)
        draw_text(cv, bx + (bw - text_w(label, 1)) // 2, 110, label, 1, GREY)
        draw_text(cv, bx + (bw - text_w(value, 3)) // 2, 120, value, 3, RED)
        draw_text(cv, bx + (bw - text_w(note, 1)) // 2, 142, note, 1, INK)

    # heroes
    hw = 330
    for i, (l1, l2, sublines, _r, _f) in enumerate(HEROES):
        hx = 8 + i * (hw + 8)
        hy = 158
        hh = 168
        cv.frame(hx, hy, hw, hh, INK, 2)
        SCENES[HERO_SCENES[i]](cv, hx + 2, hy + 2, hw - 4, 62)
        cv.hline(hx + 2, hy + 64, hw - 4, INK, 1)
        draw_text(cv, hx + 8, hy + 70, l1, 3, INK)
        draw_text(cv, hx + 8, hy + 97, l2, 3, INK)
        yy = hy + 128
        for sl in sublines:
            draw_text(cv, hx + 8, yy, sl, 2, RED)
            yy += 18

    # illustrated leads: two rows of six
    cw = 161
    for row in range(2):
        for col in range(6):
            k = row * 6 + col
            head, deck, scene, _r, _f = LEADS[k]
            cx = 8 + col * (cw + 8)
            cy = 334 + row * 138
            cv.frame(cx, cy, cw, 130, INK, 1)
            SCENES[scene](cv, cx + 1, cy + 1, cw - 2, 60)
            cv.hline(cx + 1, cy + 61, cw - 2, INK, 1)
            draw_text(cv, cx + 5, cy + 65, scene, 1, RED)
            lines = wrap(head, 2, cw - 10)[:3]
            draw_lines(cv, cx + 5, cy + 76, lines, 2, INK, 18)

    # sketch world map with numbered pins
    mx, my, mw, mh = 8, 610, 640, 148
    cv.frame(mx, my, mw, mh, INK, 1)
    cell_w = mw // 48
    cell_h = mh // 24
    for r, rowstr in enumerate(MAP_ROWS):
        for c, ch in enumerate(rowstr):
            if ch == "#":
                cv.disc(mx + c * cell_w + cell_w // 2,
                        my + r * cell_h + cell_h // 2, 2, NAVY)
    for num, name, fx, fy in MAP_PINS:
        px = mx + int(fx * mw)
        py = my + int(fy * mh)
        cv.disc(px, py, 7, RED)
        draw_text(cv, px - 2, py - 3, str(num), 1, WHITE)
    draw_text(cv, mx + 8, my + mh - 18,
              "1 KYIV  2 WARSAW  3 WELLINGTON  4 LAS VEGAS", 1, INK)
    draw_text(cv, mx + 8, my + mh - 9,
              "5 GAZA  6 CONGO  7 RIYADH  8 TALLINN", 1, INK)

    # counts panel
    px0, py0, pw = 656, 610, 360
    cv.frame(px0, py0, pw, 148, INK, 1)
    draw_text(cv, px0 + 8, py0 + 6, "THE DAY IN NUMBERS", 2, INK)
    yy = py0 + 26
    for label, code in REGIONS:
        draw_text(cv, px0 + 8, yy, label, 1, INK)
        cnt = reg.get(code, 0)
        cv.rect(px0 + 92, yy + 1, cnt * 13, 5, TEAL)
        draw_text(cv, px0 + 92 + cnt * 13 + 5, yy, str(cnt), 1, INK)
        yy += 10
    yy += 2
    for label, code in FIELDS:
        draw_text(cv, px0 + 8, yy, label, 1, INK)
        cnt = fld.get(code, 0)
        cv.rect(px0 + 92, yy + 1, cnt * 13, 5, GOLD)
        draw_text(cv, px0 + 92 + cnt * 13 + 5, yy, str(cnt), 1, INK)
        yy += 10

    # briefs
    draw_text(cv, 8, 766, "MORE FROM THE DAY", 2, RED)
    cv.hline(8, 782, W - 16, INK, 1)
    cv.vline(512, 790, 196, GREY, 1)
    for i, (txt, _r, _f) in enumerate(BRIEFS):
        col = i // 14
        row = i % 14
        bx = 8 + col * 508
        by = 790 + row * 14
        cv.rect(bx, by + 4, 4, 4, RED)
        draw_text(cv, bx + 10, by, txt, 2, INK)

    # footer: date check
    cv.hline(8, 988, W - 16, INK, 1)
    draw_text(cv, 8, 994,
              "NOT TODAY: THE ICJ MYANMAR RULING WAS 19 NOV - THE SHENZHEN "
              "TRILATERAL WAS 19 NOV - THE ANTHROPIC DEBUT WAS 19 NOV.",
              1, GREY)
    draw_text(cv, 8, 1004,
              "ALL %d STORIES HAPPENED OR WERE FIRST REPORTED ON SATURDAY "
              "21 NOVEMBER 2026." % n, 1, GREY)
    return cv


def main():
    cv = build()
    data = png_bytes(cv)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(dst, "wb") as fh:
        fh.write(data)
    print("wrote", dst, len(data), "bytes", cv.w, "x", cv.h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
