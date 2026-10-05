import os
import zlib
import struct
import math
from datetime import datetime

from src.theme import (
    CANVAS_WIDTH, CANVAS_HEIGHT, BG_COLOR, BORDER_COLOR,
    INNER_BORDER_COLOR, TEXT_COLOR, TEXT_MUTED, ACCENT_PINK,
    CONTRIBUTION_COLORS, LEVEL_MAP, GRID_START_X, GRID_START_Y,
    CELL_SIZE, CELL_GAP, CELL_RADIUS, DISPLAY_WEEKDAYS
)

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join([c*2 for c in hex_code])
    return (int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16))

# Clean 6x8 bitmap font matrix for crisp, readable labels
FONT_6X8 = {
    ' ': ["000000", "000000", "000000", "000000", "000000", "000000", "000000", "000000"],
    'A': ["001100", "010010", "100001", "100001", "111111", "100001", "100001", "100001"],
    'B': ["111110", "100001", "100001", "111110", "100001", "100001", "100001", "111110"],
    'C': ["001111", "010000", "100000", "100000", "100000", "100000", "010000", "001111"],
    'D': ["111110", "100001", "100001", "100001", "100001", "100001", "100001", "111110"],
    'E': ["111111", "100000", "100000", "111110", "100000", "100000", "100000", "111111"],
    'F': ["111111", "100000", "100000", "111110", "100000", "100000", "100000", "100000"],
    'G': ["001111", "010000", "100000", "100000", "100111", "100001", "010001", "001110"],
    'H': ["100001", "100001", "100001", "111111", "100001", "100001", "100001", "100001"],
    'I': ["011110", "001100", "001100", "001100", "001100", "001100", "001100", "011110"],
    'J': ["000111", "000011", "000011", "000011", "000011", "100011", "100011", "011100"],
    'K': ["100011", "100110", "101100", "111000", "111000", "101100", "100110", "100011"],
    'L': ["100000", "100000", "100000", "100000", "100000", "100000", "100000", "111111"],
    'M': ["100001", "110011", "101101", "100001", "100001", "100001", "100001", "100001"],
    'N': ["100001", "110001", "101001", "100101", "100011", "100001", "100001", "100001"],
    'O': ["001100", "010010", "100001", "100001", "100001", "100001", "010010", "001100"],
    'P': ["111110", "100001", "100001", "111110", "100000", "100000", "100000", "100000"],
    'Q': ["001100", "010010", "100001", "100001", "100001", "100101", "010010", "001101"],
    'R': ["111110", "100001", "100001", "111110", "101100", "100110", "100011", "100001"],
    'S': ["011111", "100000", "100000", "011110", "000001", "000001", "000001", "111110"],
    'T': ["111111", "001100", "001100", "001100", "001100", "001100", "001100", "001100"],
    'U': ["100001", "100001", "100001", "100001", "100001", "100001", "110011", "011110"],
    'V': ["100001", "100001", "100001", "100001", "010010", "010010", "001100", "001100"],
    'W': ["100001", "100001", "100001", "100001", "101101", "101101", "110011", "100001"],
    'X': ["100001", "010010", "001100", "001100", "001100", "001100", "010010", "100001"],
    'Y': ["100001", "010010", "001100", "001100", "001100", "001100", "001100", "001100"],
    'Z': ["111111", "000011", "000110", "001100", "011000", "110000", "100000", "111111"],
    'a': ["000000", "000000", "011110", "000001", "011111", "100001", "100001", "011111"],
    'b': ["100000", "100000", "111110", "100001", "100001", "100001", "100001", "111110"],
    'c': ["000000", "000000", "011110", "100001", "100000", "100000", "100001", "011110"],
    'd': ["000001", "000001", "011111", "100001", "100001", "100001", "100001", "011111"],
    'e': ["000000", "000000", "011110", "100001", "111111", "100000", "100001", "011110"],
    'f': ["001110", "010001", "010000", "111110", "010000", "010000", "010000", "010000"],
    'g': ["000000", "000000", "011111", "100001", "100001", "011111", "000001", "011110"],
    'h': ["100000", "100000", "111110", "100001", "100001", "100001", "100001", "100001"],
    'i': ["001100", "000000", "011100", "001100", "001100", "001100", "001100", "011110"],
    'j': ["000110", "000000", "001110", "000110", "000110", "000110", "100110", "011100"],
    'k': ["100000", "100000", "100011", "100110", "111100", "100110", "100011", "100001"],
    'l': ["011100", "001100", "001100", "001100", "001100", "001100", "001100", "011110"],
    'm': ["000000", "000000", "110110", "101001", "101001", "101001", "101001", "101001"],
    'n': ["000000", "000000", "111110", "100001", "100001", "100001", "100001", "100001"],
    'o': ["000000", "000000", "011110", "100001", "100001", "100001", "100001", "011110"],
    'p': ["000000", "000000", "111110", "100001", "100001", "111110", "100000", "100000"],
    'q': ["000000", "000000", "011111", "100001", "100001", "011111", "000001", "000001"],
    'r': ["000000", "000000", "101110", "110001", "100000", "100000", "100000", "100000"],
    's': ["000000", "000000", "011111", "100000", "011110", "000001", "000001", "111110"],
    't': ["010000", "010000", "111110", "010000", "010000", "010000", "010001", "001110"],
    'u': ["000000", "000000", "100001", "100001", "100001", "100001", "100011", "011101"],
    'v': ["000000", "000000", "100001", "100001", "100001", "010010", "010010", "001100"],
    'w': ["000000", "000000", "100001", "100001", "100001", "101101", "110011", "100001"],
    'x': ["000000", "000000", "100001", "010010", "001100", "001100", "010010", "100001"],
    'y': ["000000", "000000", "100001", "100001", "100001", "011111", "000001", "011110"],
    'z': ["000000", "000000", "111111", "000011", "000110", "001100", "011000", "111111"],
    '0': ["001100", "010010", "100001", "100101", "101001", "100001", "010010", "001100"],
    '1': ["000100", "001100", "000100", "000100", "000100", "000100", "000100", "011110"],
    '2': ["011110", "100001", "000001", "000010", "001100", "010000", "100000", "111111"],
    '3': ["011110", "100001", "000001", "001110", "000001", "000001", "100001", "011110"],
    '4': ["000010", "000110", "001010", "010010", "111111", "000010", "000010", "000010"],
    '5': ["111111", "100000", "111110", "000001", "000001", "000001", "100001", "011110"],
    '6': ["001110", "010000", "100000", "111110", "100001", "100001", "100001", "011110"],
    '7': ["111111", "000001", "000010", "000100", "001000", "010000", "010000", "010000"],
    '8': ["011110", "100001", "100001", "011110", "100001", "100001", "100001", "011110"],
    '9': ["011110", "100001", "100001", "100001", "011111", "000001", "000010", "011100"],
    '-': ["000000", "000000", "000000", "111111", "000000", "000000", "000000", "000000"],
    '/': ["000001", "000010", "000100", "001000", "010000", "100000", "000000", "000000"],
    ':': ["000000", "001100", "001100", "000000", "001100", "001100", "000000", "000000"],
    '.': ["000000", "000000", "000000", "000000", "000000", "001100", "001100", "000000"],
    ',': ["000000", "000000", "000000", "000000", "001100", "001100", "000100", "001000"],
    '•': ["000000", "001100", "011110", "011110", "001100", "000000", "000000", "000000"],
    '●': ["001100", "011110", "111111", "111111", "011110", "001100", "000000", "000000"],
    '[': ["011100", "010000", "010000", "010000", "010000", "010000", "010000", "011100"],
    ']': ["001110", "000010", "000010", "000010", "000010", "000010", "000010", "001110"],
}

class PureCanvas:
    """High-performance 32-bit RGBA Pure Python rasterizer & PNG encoder."""
    def __init__(self, width, height, bg_hex):
        self.width = width
        self.height = height
        bg_rgb = hex_to_rgb(bg_hex)
        bg_bytes = bytes([bg_rgb[0], bg_rgb[1], bg_rgb[2], 255])
        self.pixels = bytearray(bg_bytes * (width * height))

    def set_pixel(self, x, y, r, g, b, a=255, alpha=None):
        if alpha is not None:
            a = alpha
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = (y * self.width + x) * 4
            if a == 255:
                self.pixels[idx:idx+4] = bytes([r, g, b, 255])
            else:
                sa = a / 255.0
                da = self.pixels[idx+3] / 255.0
                out_a = sa + da * (1.0 - sa)
                if out_a > 0:
                    pr = int((r * sa + self.pixels[idx] * da * (1.0 - sa)) / out_a)
                    pg = int((g * sa + self.pixels[idx+1] * da * (1.0 - sa)) / out_a)
                    pb = int((b * sa + self.pixels[idx+2] * da * (1.0 - sa)) / out_a)
                    self.pixels[idx:idx+4] = bytes([pr, pg, pb, int(out_a * 255)])

    def fill_rect(self, x, y, w, h, color_hex, alpha=255):
        r, g, b = hex_to_rgb(color_hex)
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(self.width, x + w)
        y2 = min(self.height, y + h)
        if x2 <= x1 or y2 <= y1:
            return
        row_w = x2 - x1
        if alpha == 255:
            color_bytes = bytes([r, g, b, 255]) * row_w
            for py in range(y1, y2):
                idx = (py * self.width + x1) * 4
                self.pixels[idx:idx + row_w * 4] = color_bytes
        else:
            for py in range(y1, y2):
                for px in range(x1, x2):
                    self.set_pixel(px, py, r, g, b, a=alpha)

    def fill_rounded_rect(self, x, y, w, h, radius, fill_hex, border_hex=None, border_width=1):
        rad = min(radius, w // 2, h // 2)
        if rad <= 0:
            self.fill_rect(x, y, w, h, fill_hex)
            if border_hex and border_width > 0:
                self.fill_rect(x, y, w, border_width, border_hex)
                self.fill_rect(x, y + h - border_width, w, border_width, border_hex)
                self.fill_rect(x, y, border_width, h, border_hex)
                self.fill_rect(x + w - border_width, y, border_width, h, border_hex)
            return

        # Interior slabs
        self.fill_rect(x, y + rad, w, h - 2 * rad, fill_hex)
        self.fill_rect(x + rad, y, w - 2 * rad, rad, fill_hex)
        self.fill_rect(x + rad, y + h - rad, w - 2 * rad, rad, fill_hex)

        # Corners
        corners = [
            (x + rad, y + rad, range(x, x + rad), range(y, y + rad)),
            (x + w - rad, y + rad, range(x + w - rad, x + w), range(y, y + rad)),
            (x + rad, y + h - rad, range(x, x + rad), range(y + h - rad, y + h)),
            (x + w - rad, y + h - rad, range(x + w - rad, x + w), range(y + h - rad, y + h))
        ]
        
        rad_sq = rad * rad
        inner_rad_sq = max(0, rad - border_width) ** 2
        r_f, g_f, b_f = hex_to_rgb(fill_hex)
        r_b, g_b, b_b = hex_to_rgb(border_hex) if border_hex else (0, 0, 0)

        for cx, cy, x_range, y_range in corners:
            for py in y_range:
                for px in x_range:
                    dist_sq = (px - cx)**2 + (py - cy)**2
                    if dist_sq <= rad_sq:
                        if border_hex and dist_sq > inner_rad_sq:
                            self.set_pixel(px, py, r_b, g_b, b_b)
                        else:
                            self.set_pixel(px, py, r_f, g_f, b_f)

        # Border strokes
        if border_hex and border_width > 0:
            self.fill_rect(x + rad, y, w - 2 * rad, border_width, border_hex)
            self.fill_rect(x + rad, y + h - border_width, w - 2 * rad, border_width, border_hex)
            self.fill_rect(x, y + rad, border_width, h - 2 * rad, border_hex)
            self.fill_rect(x + w - border_width, y + rad, border_width, h - 2 * rad, border_hex)

    def draw_line(self, x0, y0, x1, y1, color_hex, width=1, alpha=255):
        r, g, b = hex_to_rgb(color_hex)
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        half_w = width // 2
        while True:
            for wx in range(-half_w, half_w + 1):
                for wy in range(-half_w, half_w + 1):
                    self.set_pixel(x0 + wx, y0 + wy, r, g, b, a=alpha)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_circle(self, cx, cy, radius, fill_hex, border_hex=None, alpha=255):
        rf, gf, bf = hex_to_rgb(fill_hex)
        rb, gb, bb = hex_to_rgb(border_hex) if border_hex else (0, 0, 0)
        r_sq = radius * radius
        
        for dy in range(-radius, radius + 1):
            py = cy + dy
            if 0 <= py < self.height:
                half_span = int(math.isqrt(max(0, r_sq - dy*dy)))
                x_start = max(0, cx - half_span)
                x_end = min(self.width, cx + half_span + 1)
                for px in range(x_start, x_end):
                    d_sq = (px - cx)**2 + dy*dy
                    if border_hex and d_sq > (radius - 1)**2:
                        self.set_pixel(px, py, rb, gb, bb, a=alpha)
                    else:
                        self.set_pixel(px, py, rf, gf, bf, a=alpha)

    def fill_polygon(self, points, color_hex, alpha=255):
        if len(points) < 3:
            return
        r, g, b = hex_to_rgb(color_hex)
        min_y = max(0, min(p[1] for p in points))
        max_y = min(self.height - 1, max(p[1] for p in points))
        
        for y in range(min_y, max_y + 1):
            nodes = []
            j = len(points) - 1
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[j]
                if (p1[1] < y and p2[1] >= y) or (p2[1] < y and p1[1] >= y):
                    x_intersect = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                    nodes.append(x_intersect)
                j = i
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                x_start = max(0, int(nodes[k]))
                x_end = min(self.width, int(nodes[k+1]) + 1)
                for x in range(x_start, x_end):
                    self.set_pixel(x, y, r, g, b, a=alpha)

    def draw_blossom(self, cx, cy, radius=6):
        petal_color = "#FFA8C5"
        center_color = "#FFFFFF"
        pistil_color = "#C11E66"
        petal_rad = max(2, int(radius * 0.8))
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2
            px = int(cx + math.cos(angle) * (radius * 0.65))
            py = int(cy + math.sin(angle) * (radius * 0.65))
            self.draw_circle(px, py, petal_rad, petal_color, alpha=225)
        self.draw_circle(cx, cy, max(1, int(radius * 0.4)), center_color, alpha=255)
        self.draw_circle(cx, cy, max(1, int(radius * 0.2)), pistil_color, alpha=255)

    def draw_falling_petal(self, cx, cy, size=4, angle=0.4):
        color = "#FFAEC9"
        r, g, b = hex_to_rgb(color)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        for dy in range(-size, size + 1):
            for dx in range(-size // 2, size // 2 + 1):
                if (dx*2)**2 + dy**2 <= size**2:
                    rx = int(cx + dx * cos_a - dy * sin_a)
                    ry = int(cy + dx * sin_a + dy * cos_a)
                    self.set_pixel(rx, ry, r, g, b, a=200)

    def draw_text(self, text, x, y, color_hex, scale=1):
        r, g, b = hex_to_rgb(color_hex)
        curr_x = x
        for ch in text:
            glyph = FONT_6X8.get(ch, FONT_6X8.get(' '))
            if glyph:
                for row_idx, row in enumerate(glyph):
                    for col_idx, bit in enumerate(row):
                        if bit == '1':
                            if scale == 1:
                                self.set_pixel(curr_x + col_idx, y + row_idx, r, g, b)
                            else:
                                for sx in range(scale):
                                    for sy in range(scale):
                                        self.set_pixel(curr_x + col_idx * scale + sx, y + row_idx * scale + sy, r, g, b)
            curr_x += (6 + 1) * scale

    def to_png_bytes(self):
        raw_rows = bytearray()
        stride = self.width * 4
        for y in range(self.height):
            raw_rows.append(0)
            start = y * stride
            raw_rows.extend(self.pixels[start:start+stride])
            
        compressed = zlib.compress(bytes(raw_rows), 6)
        
        def make_chunk(chunk_type, data):
            crc = zlib.crc32(chunk_type + data) & 0xffffffff
            return struct.pack('>I', len(data)) + chunk_type + data + struct.pack('>I', crc)
            
        out = bytearray(b'\x89PNG\r\n\x1a\n')
        out.extend(make_chunk(b'IHDR', struct.pack('>IIBBBBB', self.width, self.height, 8, 6, 0, 0, 0)))
        out.extend(make_chunk(b'IDAT', compressed))
        out.extend(make_chunk(b'IEND', b''))
        return bytes(out)

def draw_background_and_frame(canvas):
    """Layer 1: Canvas background, thick rounded black border, subtle inner border."""
    # Outer Rounded Frame (3px solid #1A1A1A) with radius 18
    canvas.fill_rounded_rect(3, 3, CANVAS_WIDTH - 6, CANVAS_HEIGHT - 6, 18, BG_COLOR, border_hex=BORDER_COLOR, border_width=3)
    
    # Inner Decorative Border (1px hairline #ECDCE4)
    canvas.fill_rounded_rect(10, 10, CANVAS_WIDTH - 20, CANVAS_HEIGHT - 20, 12, BG_COLOR, border_hex=INNER_BORDER_COLOR, border_width=1)

def draw_artwork(canvas):
    """Layer 2: Japanese Sakura Scenery (Sun, Fuji, Pagoda, Water, Tree & Blossoms)."""
    # 1. Soft Warm Pink Sun/Moon in upper-left
    canvas.draw_circle(145, 95, 42, "#FCE6EE", border_hex="#FCEFF4", alpha=220)
    canvas.draw_circle(145, 95, 34, "#FBDCE6", alpha=240)

    # 2. Distant Mount Fuji / Japanese Alps
    fuji_points = [(40, 240), (130, 165), (160, 165), (255, 240)]
    canvas.fill_polygon(fuji_points, "#E4CEE0", alpha=180)
    
    # Snowcap on summit
    snow_points = [(120, 178), (130, 165), (160, 165), (170, 178), (155, 174), (145, 178), (135, 173)]
    canvas.fill_polygon(snow_points, "#FFFFFF", alpha=240)

    # Secondary mountain ridge
    ridge_points = [(170, 240), (220, 195), (275, 240)]
    canvas.fill_polygon(ridge_points, "#DAC2D5", alpha=200)

    # 3. Calm Water & Reflections
    canvas.fill_rect(12, 240, 250, 95, "#F7E8F1", alpha=200)
    for ry in [250, 260, 272, 285, 300, 318]:
        canvas.draw_line(25, ry, 110, ry, "#FFFFFF", width=1, alpha=160)
        canvas.draw_line(135, ry + 4, 230, ry + 4, "#F4D2E5", width=1, alpha=140)

    # 4. Subtle Pagoda Silhouette
    pagoda_tier1 = [(200, 235), (202, 215), (228, 215), (230, 235)]
    canvas.fill_polygon(pagoda_tier1, "#5E4352")
    roof1 = [(194, 216), (215, 207), (236, 216)]
    canvas.fill_polygon(roof1, "#4E3643")
    
    pagoda_tier2 = [(204, 207), (206, 192), (224, 192), (226, 207)]
    canvas.fill_polygon(pagoda_tier2, "#5E4352")
    roof2 = [(198, 193), (215, 185), (232, 193)]
    canvas.fill_polygon(roof2, "#4E3643")
    
    pagoda_tier3 = [(208, 185), (210, 175), (220, 175), (222, 185)]
    canvas.fill_polygon(pagoda_tier3, "#5E4352")
    roof3 = [(202, 176), (215, 169), (228, 176)]
    canvas.fill_polygon(roof3, "#4E3643")
    
    # Pagoda spire (sōrin)
    canvas.draw_line(215, 169, 215, 150, "#3E2B36", width=2)
    canvas.draw_circle(215, 150, 2, "#C11E66")

    # 5. Hero Sakura Tree Branches (entering from upper-left, staying inside frame)
    bark = "#321E25"
    sub_bark = "#492F3B"
    # Main trunk
    canvas.draw_line(12, 12, 50, 45, bark, width=8)
    canvas.draw_line(50, 45, 95, 65, bark, width=6)
    canvas.draw_line(95, 65, 155, 75, bark, width=5)
    canvas.draw_line(155, 75, 215, 80, bark, width=4)
    canvas.draw_line(215, 80, 245, 82, sub_bark, width=2)

    # Sub-branch 1 (upper reach)
    canvas.draw_line(50, 45, 75, 25, bark, width=4)
    canvas.draw_line(75, 25, 125, 20, sub_bark, width=3)
    canvas.draw_line(125, 20, 180, 22, sub_bark, width=2)

    # Sub-branch 2 (lower reach)
    canvas.draw_line(95, 65, 120, 105, sub_bark, width=4)
    canvas.draw_line(120, 105, 155, 135, sub_bark, width=2)
    canvas.draw_line(155, 135, 185, 150, sub_bark, width=1)

    # 6. Dense Realistic Cherry Blossom Clusters
    blossom_coords = [
        (35, 38), (55, 28), (75, 20), (100, 18), (125, 16), (150, 18), (175, 22), (200, 28),
        (65, 52), (85, 60), (110, 68), (135, 72), (160, 75), (185, 78), (210, 80), (235, 82),
        (105, 90), (120, 105), (135, 120), (155, 135), (175, 145),
        (28, 55), (45, 75), (70, 95), (90, 115),
        (140, 50), (165, 55), (190, 60), (215, 65),
        (22, 22), (32, 15), (50, 12), (80, 42), (115, 45)
    ]
    for bx, by in blossom_coords:
        canvas.draw_blossom(bx, by, radius=7)
        canvas.draw_circle(bx - 5, by + 4, 3, "#FFC0D8", alpha=220)
        canvas.draw_circle(bx + 6, by - 4, 2, "#FFA0C2", alpha=240)

    # 7. Tasteful Falling Petals (Outside the contribution grid!)
    petals = [
        (45, 160, 4, 0.3), (70, 190, 5, 0.7), (95, 225, 4, 0.2),
        (130, 260, 5, 0.9), (160, 290, 4, 0.4), (200, 310, 5, 0.8),
        (240, 320, 4, 0.5), (280, 315, 4, 0.6), (330, 325, 5, 0.3),
        (235, 105, 3, 0.5), (245, 130, 4, 0.8)
    ]
    for px, py, psize, pang in petals:
        canvas.draw_falling_petal(px, py, size=psize, angle=pang)

def draw_contribution_grid(canvas, calendar_data):
    """Layer 3: Renders the 52/53 weeks × 7 days heatmap grid with real counts and colors."""
    weeks = calendar_data.get("weeks", [])

    # Calculate month labels dynamically based on real contribution dates
    month_positions = []
    last_month = None
    for w_idx, week in enumerate(weeks):
        for day in week.get("contributionDays", []):
            d_str = day.get("date", "")
            if d_str:
                dt = datetime.strptime(d_str, "%Y-%m-%d")
                m_str = dt.strftime("%b")
                if m_str != last_month:
                    last_month = m_str
                    col_x = GRID_START_X + w_idx * (CELL_SIZE + CELL_GAP)
                    month_positions.append((col_x, m_str))
                break

    # Draw month labels
    for mx, mname in month_positions:
        canvas.draw_text(mname, mx, GRID_START_Y - 18, TEXT_MUTED, scale=1)

    # Draw weekday labels on the left of grid
    for row_idx, label in DISPLAY_WEEKDAYS.items():
        wy = GRID_START_Y + row_idx * (CELL_SIZE + CELL_GAP) + 3
        canvas.draw_text(label, GRID_START_X - 28, wy, TEXT_MUTED, scale=1)

    # Render all contribution cells
    for w_idx, week in enumerate(weeks):
        col_x = GRID_START_X + w_idx * (CELL_SIZE + CELL_GAP)
        for day in week.get("contributionDays", []):
            gh_weekday = day.get("weekday", 0)
            row_y = GRID_START_Y + gh_weekday * (CELL_SIZE + CELL_GAP)
            
            level_str = day.get("contributionLevel", "NONE")
            lvl = LEVEL_MAP.get(level_str, 0)
            count = day.get("contributionCount", 0)
            if lvl == 0 and count > 0:
                lvl = 1
            lvl = min(4, max(0, lvl))
            
            cell_color = CONTRIBUTION_COLORS[lvl]
            border_c = "#F0E2E8" if lvl == 0 else None
            
            canvas.fill_rounded_rect(
                col_x, row_y, CELL_SIZE, CELL_SIZE, CELL_RADIUS,
                cell_color, border_hex=border_c, border_width=1
            )

    # Draw Legend at bottom right
    legend_y = GRID_START_Y + 7 * (CELL_SIZE + CELL_GAP) + 16
    legend_x = 940
    canvas.draw_text("Less", legend_x, legend_y + 3, TEXT_MUTED, scale=1)
    
    start_box_x = legend_x + 35
    for i in range(5):
        bx = start_box_x + i * (CELL_SIZE + 3)
        bcolor = CONTRIBUTION_COLORS[i]
        b_border = "#F0E2E8" if i == 0 else None
        canvas.fill_rounded_rect(bx, legend_y, CELL_SIZE, CELL_SIZE, CELL_RADIUS, bcolor, border_hex=b_border, border_width=1)
        
    canvas.draw_text("More", start_box_x + 5 * (CELL_SIZE + 3) + 8, legend_y + 3, TEXT_MUTED, scale=1)

def draw_header_text(canvas, username, total_contributions):
    """Layer 4: Title, stats, and live status badge on top."""
    # Top Brand / Title
    canvas.draw_circle(GRID_START_X + 12, 50, 12, "#FDE8F1", border_hex=ACCENT_PINK)
    canvas.draw_text("S", GRID_START_X + 9, 46, ACCENT_PINK, scale=1)

    title_text = f"{username} / SAKURA CONTRIBUTION GARDEN"
    canvas.draw_text(title_text, GRID_START_X + 32, 44, TEXT_COLOR, scale=2)

    subtitle_text = f"{total_contributions} contributions in the last year  -  Daily Live Sync"
    canvas.draw_text(subtitle_text, GRID_START_X + 32, 70, TEXT_MUTED, scale=1)

    # Active status badge on upper-right
    badge_x = 1005
    badge_y = 44
    canvas.fill_rounded_rect(badge_x, badge_y, 85, 24, 6, "#FAF0F5", border_hex="#F0D0E0", border_width=1)
    canvas.draw_circle(badge_x + 14, badge_y + 12, 4, "#2EB872")
    canvas.draw_text("SYNCED", badge_x + 24, badge_y + 8, TEXT_MUTED, scale=1)

def render_png(calendar_data, output_path):
    """
    Renders high-quality PNG visualization for GitHub profile.
    Properly layered: Frame -> Artwork -> Heatmap Grid -> Header Text.
    """
    username = calendar_data.get("username", "SamSurve")
    total_contributions = calendar_data.get("total_contributions", 0)

    # Initialize canvas
    canvas = PureCanvas(CANVAS_WIDTH, CANVAS_HEIGHT, BG_COLOR)

    # Layer 1: Frame and Canvas Background
    draw_background_and_frame(canvas)

    # Layer 2: Japanese Sakura Artwork (Upper-left & background)
    draw_artwork(canvas)

    # Layer 3: Contribution Heatmap Grid (Hero central/right)
    draw_contribution_grid(canvas, calendar_data)

    # Layer 4: Framing chrome, title, and live stats
    draw_header_text(canvas, username, total_contributions)

    # Encode and write PNG
    png_data = canvas.to_png_bytes()
    
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_path, "wb") as f:
        f.write(png_data)

    return os.path.abspath(output_path)
