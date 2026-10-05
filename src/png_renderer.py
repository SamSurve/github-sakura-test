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
        petal_color = "#FFA6C4"
        center_color = "#FFFFFF"
        pistil_color = "#C11E66"
        petal_rad = max(2, int(radius * 0.8))
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2
            px = int(cx + math.cos(angle) * (radius * 0.65))
            py = int(cy + math.sin(angle) * (radius * 0.65))
            self.draw_circle(px, py, petal_rad, petal_color, alpha=230)
        self.draw_circle(cx, cy, max(1, int(radius * 0.42)), center_color, alpha=255)
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
                    self.set_pixel(rx, ry, r, g, b, a=190)

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
    # Outer Rounded Frame (3px solid #1A1A1A) with radius 16
    canvas.fill_rounded_rect(3, 3, CANVAS_WIDTH - 6, CANVAS_HEIGHT - 6, 16, BG_COLOR, border_hex=BORDER_COLOR, border_width=3)
    
    # Inner Decorative Border (1px hairline #ECDCE4)
    canvas.fill_rounded_rect(9, 9, CANVAS_WIDTH - 18, CANVAS_HEIGHT - 18, 11, BG_COLOR, border_hex=INNER_BORDER_COLOR, border_width=1)

def draw_artwork(canvas):
    """Layer 2: Japanese Sakura Scenery framing the canvas naturally without competing with the grid."""
    # 1. Soft Warm Pink Sun/Moon behind mountain in upper-left
    canvas.draw_circle(105, 75, 36, "#FDE2EC", border_hex="#FCECF2", alpha=210)
    canvas.draw_circle(105, 75, 28, "#FBD5E3", alpha=230)

    # 2. Distant Mount Fuji / Japanese Mountain Ridge (Sweeping majestic silhouette)
    fuji_points = [(10, 275), (85, 142), (120, 142), (220, 275)]
    canvas.fill_polygon(fuji_points, "#E4CEE0", alpha=190)
    
    # Snowcap on Mount Fuji
    snow_points = [(78, 155), (85, 142), (120, 142), (128, 155), (115, 151), (105, 156), (95, 150)]
    canvas.fill_polygon(snow_points, "#FFFFFF", alpha=245)

    # Secondary softer mountain ridge running into midground
    ridge_points = [(130, 275), (185, 205), (255, 275)]
    canvas.fill_polygon(ridge_points, "#D9C1D5", alpha=180)

    # 3. Soft Shoreline & Gentle Water Wash (Undulating, organic shoreline)
    shoreline_points = [
        (10, 260), (120, 255), (280, 268), (520, 265), (780, 270), 
        (1020, 265), (1188, 270), (1188, 338), (10, 338)
    ]
    canvas.fill_polygon(shoreline_points, "#F7EBF2", alpha=190)

    # Delicate water ripples extending gracefully across
    for ry in [282, 295, 308, 320, 330]:
        canvas.draw_line(25, ry, 150, ry, "#FFFFFF", width=1, alpha=160)
        canvas.draw_line(175, ry + 2, 400, ry + 2, "#F2D5E7", width=1, alpha=120)
        canvas.draw_line(450, ry, 750, ry, "#FFFFFF", width=1, alpha=110)
        canvas.draw_line(800, ry + 3, 1150, ry + 3, "#F2D5E7", width=1, alpha=120)

    # 4. Traditional Pagoda Silhouette nestled into shoreline
    pagoda_tier1 = [(138, 265), (140, 248), (160, 248), (162, 265)]
    canvas.fill_polygon(pagoda_tier1, "#543A49")
    roof1 = [(132, 249), (150, 241), (168, 249)]
    canvas.fill_polygon(roof1, "#442D3B")
    
    pagoda_tier2 = [(141, 241), (143, 228), (157, 228), (159, 241)]
    canvas.fill_polygon(pagoda_tier2, "#543A49")
    roof2 = [(136, 229), (150, 222), (164, 229)]
    canvas.fill_polygon(roof2, "#442D3B")
    
    pagoda_tier3 = [(144, 222), (146, 212), (154, 212), (156, 222)]
    canvas.fill_polygon(pagoda_tier3, "#543A49")
    roof3 = [(139, 213), (150, 207), (161, 213)]
    canvas.fill_polygon(roof3, "#442D3B")
    
    # Pagoda finial spire (sōrin)
    canvas.draw_line(150, 207, 150, 190, "#36222E", width=2)
    canvas.draw_circle(150, 190, 2, "#C11E66")

    # 5. Hero Sakura Tree Branches (Upper-left, framing top-left)
    bark = "#2D1822"
    sub_bark = "#462B37"
    # Main upper-left trunk
    canvas.draw_line(10, 10, 42, 38, bark, width=8)
    canvas.draw_line(42, 38, 85, 50, bark, width=6)
    canvas.draw_line(85, 50, 130, 54, bark, width=5)
    canvas.draw_line(130, 54, 168, 52, sub_bark, width=3)

    # Sub-branch upper
    canvas.draw_line(42, 38, 68, 18, bark, width=4)
    canvas.draw_line(68, 18, 110, 14, sub_bark, width=2)

    # Sub-branch lower reaching toward pagoda
    canvas.draw_line(85, 50, 102, 80, sub_bark, width=3)
    canvas.draw_line(102, 80, 122, 108, sub_bark, width=2)

    # 6. Upper-Left Blossom Clusters
    blossoms_left = [
        (28, 30), (46, 22), (66, 16), (88, 14), (112, 14), (135, 16),
        (52, 42), (72, 48), (94, 52), (116, 53), (140, 53), (162, 51),
        (88, 70), (102, 85), (115, 100), (128, 114),
        (20, 16), (36, 10), (14, 36), (32, 52), (56, 65)
    ]
    for bx, by in blossoms_left:
        canvas.draw_blossom(bx, by, radius=7)
        canvas.draw_circle(bx - 4, by + 3, 2, "#FFC0D8", alpha=220)
        canvas.draw_circle(bx + 5, by - 3, 2, "#FFA0C2", alpha=240)

    # 7. Right-Side Framing Sprig (Eliminates the empty white space on right!)
    canvas.draw_line(1188, 12, 1155, 32, bark, width=4)
    canvas.draw_line(1155, 32, 1120, 42, sub_bark, width=3)
    canvas.draw_line(1155, 32, 1140, 58, sub_bark, width=2)
    blossoms_right = [
        (1175, 18), (1155, 26), (1135, 36), (1118, 42), (1138, 55), (1155, 62), (1178, 40)
    ]
    for bx, by in blossoms_right:
        canvas.draw_blossom(bx, by, radius=6)
        canvas.draw_circle(bx - 3, by + 3, 2, "#FFC0D8", alpha=220)

    # 8. Subtle Japanese Stone Lantern (tōrō) silhouette on lower right
    lx = 1150
    ly = 275
    canvas.fill_polygon([(lx-4, ly+20), (lx+4, ly+20), (lx+3, ly+8), (lx-3, ly+8)], "#5A4250", alpha=180) # Base & shaft
    canvas.fill_polygon([(lx-6, ly+8), (lx+6, ly+8), (lx+5, ly+2), (lx-5, ly+2)], "#4D3643", alpha=200)   # Light chamber
    canvas.fill_polygon([(lx-8, ly+2), (lx+8, ly+2), (lx, ly-4)], "#3E2B36", alpha=220)                   # Roof cap
    canvas.draw_circle(lx, ly-4, 2, "#C11E66", alpha=220)                                                 # Jewel finial

    # 9. Delicate Falling Petals (Scattered tastefully, never covering cells)
    petals = [
        (35, 135, 4, 0.3), (52, 180, 4, 0.7), (75, 215, 5, 0.2),
        (98, 250, 4, 0.9), (128, 285, 4, 0.4), (200, 300, 5, 0.8),
        (330, 310, 4, 0.5), (520, 315, 4, 0.6), (720, 310, 5, 0.3),
        (880, 305, 4, 0.5), (1020, 300, 4, 0.8), (1145, 105, 3, 0.4),
        (1130, 140, 4, 0.7)
    ]
    for px, py, psize, pang in petals:
        canvas.draw_falling_petal(px, py, size=psize, angle=pang)

def draw_header_bar(canvas, username, total_contributions):
    """Layer 3: Minimal, clean, editorial Japanese header bar (perfectly aligned with grid)."""
    # Left: User branding
    canvas.draw_circle(GRID_START_X + 6, 38, 8, "#FDE8F1", border_hex=ACCENT_PINK)
    canvas.draw_text("S", GRID_START_X + 4, 34, ACCENT_PINK, scale=1)
    
    header_user = f"{username}"
    canvas.draw_text(header_user, GRID_START_X + 20, 34, TEXT_COLOR, scale=1)
    
    user_end_x = GRID_START_X + 20 + len(header_user) * 7
    canvas.draw_text("•", user_end_x + 8, 34, TEXT_MUTED, scale=1)
    
    stats_text = f"{total_contributions} contributions in the last year  •  Daily Live Sync"
    canvas.draw_text(stats_text, user_end_x + 22, 34, TEXT_MUTED, scale=1)

    # Right: Compact Live status indicator (Aligned with right grid edge: 1126 - 75 = 1051)
    badge_x = 1051
    badge_y = 28
    canvas.fill_rounded_rect(badge_x, badge_y, 75, 20, 5, "#FAF0F5", border_hex="#F0D0E0", border_width=1)
    canvas.draw_circle(badge_x + 10, badge_y + 10, 3, "#2EB872")
    canvas.draw_text("SYNCED", badge_x + 19, badge_y + 6, TEXT_MUTED, scale=1)

def draw_contribution_grid(canvas, calendar_data):
    """Layer 4: HERO Heatmap Grid (Visually dominant, aligned, readable)."""
    weeks = calendar_data.get("weeks", [])

    # Calculate month positions dynamically based on real contribution dates
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

    # Draw month labels directly above the grid (centered over column)
    for mx, mname in month_positions:
        canvas.draw_text(mname, mx - 2, GRID_START_Y - 17, TEXT_MUTED, scale=1)

    # Draw weekday labels on the left of grid (vertically centered on rows)
    for row_idx, label in DISPLAY_WEEKDAYS.items():
        wy = GRID_START_Y + row_idx * (CELL_SIZE + CELL_GAP) + 3
        canvas.draw_text(label, GRID_START_X - 30, wy, TEXT_MUTED, scale=1)

    # Render all contribution cells with real counts and 5-tier pink levels
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
            border_c = "#EFE0E6" if lvl == 0 else None
            
            canvas.fill_rounded_rect(
                col_x, row_y, CELL_SIZE, CELL_SIZE, CELL_RADIUS,
                cell_color, border_hex=border_c, border_width=1
            )

    # Draw Legend directly below the grid (right-aligned with grid end at X=1126)
    grid_bottom_y = GRID_START_Y + 7 * (CELL_SIZE + CELL_GAP)
    legend_y = grid_bottom_y + 12
    legend_x = 984
    canvas.draw_text("Less", legend_x, legend_y + 3, TEXT_MUTED, scale=1)
    
    start_box_x = legend_x + 35
    box_size = 12
    for i in range(5):
        bx = start_box_x + i * (box_size + 3)
        bcolor = CONTRIBUTION_COLORS[i]
        b_border = "#EFE0E6" if i == 0 else None
        canvas.fill_rounded_rect(bx, legend_y + 1, box_size, box_size, 2, bcolor, border_hex=b_border, border_width=1)
        
    canvas.draw_text("More", start_box_x + 5 * (box_size + 3) + 8, legend_y + 3, TEXT_MUTED, scale=1)

def render_png(calendar_data, output_path):
    """
    Renders the redesigned premium Sakura contribution banner PNG.
    Grid is the prominent hero, beautifully framed by Japanese landscape & flora.
    """
    username = calendar_data.get("username", "SamSurve")
    total_contributions = calendar_data.get("total_contributions", 0)

    # Initialize canvas
    canvas = PureCanvas(CANVAS_WIDTH, CANVAS_HEIGHT, BG_COLOR)

    # Layer 1: Frame and Canvas Background
    draw_background_and_frame(canvas)

    # Layer 2: Japanese Sakura Landscape Artwork (Background & Framing)
    draw_artwork(canvas)

    # Layer 3: Minimal, clean, non-intrusive header bar
    draw_header_bar(canvas, username, total_contributions)

    # Layer 4: Contribution Heatmap Grid (THE HERO - visually dominant)
    draw_contribution_grid(canvas, calendar_data)

    # Encode and write PNG
    png_data = canvas.to_png_bytes()
    
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_path, "wb") as f:
        f.write(png_data)

    return os.path.abspath(output_path)
