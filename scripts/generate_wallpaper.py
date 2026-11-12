#!/usr/bin/env python3
"""
Generates the custom high-definition Victor Cyberpunk Workstation Wallpaper (1920x1080).
Follows the exact design system: #080C0B, #111820, #39FF88, #00D9FF, #D6E5DF.
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
OUT_FILE = Path("/home/alpha/victor-command-center/assets/victor-cyberpunk-wallpaper.png")
PIC_FILE = Path.home() / "Pictures" / "victor-cyberpunk-wallpaper.png"

im = Image.new("RGB", (W, H), (8, 12, 11))  # #080C0B
draw = ImageDraw.Draw(im)

# 1. Subtle Radial / Angular Gradient Background
cx, cy = W // 2, H // 2
for r in range(max(W, H), 0, -20):
    factor = 1.0 - (r / max(W, H))
    # Mix from #080C0B to #111820
    r_c = int(8 + (17 - 8) * factor * 0.6)
    g_c = int(12 + (24 - 12) * factor * 0.6)
    b_c = int(11 + (32 - 11) * factor * 0.6)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(r_c, g_c, b_c))

# 2. Futuristic Grid Matrix
grid_size = 60
for x in range(0, W, grid_size):
    draw.line([(x, 0), (x, H)], fill=(16, 26, 23), width=1)
for y in range(0, H, grid_size):
    draw.line([(0, y), (W, y)], fill=(16, 26, 23), width=1)

# Subtle perspective grid lines at bottom
horizon_y = int(H * 0.72)
for x in range(-W, 2 * W, 80):
    draw.line([(cx, horizon_y), (x, H)], fill=(20, 34, 28), width=1)
for y in range(horizon_y, H, 25):
    draw.line([(0, y), (W, y)], fill=(20, 36, 30), width=1)

# 3. Circuit Traces & Nodes in Cyan & Neon Green
circuits = [
    ([(100, 150), (350, 150), (450, 250), (450, 480)], (57, 255, 136)),
    ([(1820, 150), (1570, 150), (1470, 250), (1470, 520)], (0, 217, 255)),
    ([(120, 920), (380, 920), (480, 820), (700, 820)], (0, 217, 255)),
    ([(1800, 920), (1540, 920), (1440, 820), (1220, 820)], (57, 255, 136)),
    ([(cx - 300, cy - 220), (cx + 300, cy - 220)], (24, 40, 34)),
    ([(cx - 300, cy + 220), (cx + 300, cy + 220)], (24, 40, 34)),
]

for points, color in circuits:
    draw.line(points, fill=color, width=2)
    for px, py in points:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=color)

# 4. Central Cyberpunk Hexagonal Core
hex_r = 160
hex_pts = []
for i in range(6):
    angle = math.radians(60 * i - 30)
    hx = cx + int(hex_r * math.cos(angle))
    hy = cy + int(hex_r * math.sin(angle))
    hex_pts.append((hx, hy))

draw.polygon(hex_pts, fill=(14, 20, 26), outline=(0, 217, 255), width=2)

# Inner hexagon
hex_r_in = 135
hex_pts_in = []
for i in range(6):
    angle = math.radians(60 * i - 30)
    hx = cx + int(hex_r_in * math.cos(angle))
    hy = cy + int(hex_r_in * math.sin(angle))
    hex_pts_in.append((hx, hy))

draw.polygon(hex_pts_in, fill=(9, 13, 17), outline=(57, 255, 136), width=1)

# Central Emblem: Stylized V & Terminal Prompt ⚡
# Stylized 'V'
v_pts = [
    (cx - 50, cy - 65),
    (cx, cy + 45),
    (cx + 50, cy - 65),
    (cx + 28, cy - 65),
    (cx, cy - 5),
    (cx - 28, cy - 65)
]
draw.polygon(v_pts, fill=(57, 255, 136))

# Lightning Bolt / Command Center Core
bolt_pts = [
    (cx + 2, cy - 70),
    (cx - 15, cy - 35),
    (cx - 2, cy - 35),
    (cx - 8, cy - 5),
    (cx + 16, cy - 42),
    (cx + 2, cy - 42)
]
draw.polygon(bolt_pts, fill=(0, 217, 255))

# 5. Typography / Branding Texts
try:
    font_large = ImageFont.truetype("/usr/share/fonts/truetype/firacode/FiraCode-Bold.ttf", 26)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/firacode/FiraCode-Regular.ttf", 14)
    font_hud = ImageFont.truetype("/usr/share/fonts/truetype/firacode/FiraCode-Medium.ttf", 11)
except Exception:
    font_large = font_sub = font_hud = ImageFont.load_default()

# Title text below emblem
title = "VICTOR ODUOR"
bbox = draw.textbbox((0, 0), title, font=font_large)
tw = bbox[2] - bbox[0]
draw.text((cx - tw // 2, cy + 75), title, fill=(57, 255, 136), font=font_large)

sub = "// SOFTWARE DEVELOPER & ICT PROFESSIONAL // KALI ROLLING WORKSTATION"
bbox_s = draw.textbbox((0, 0), sub, font=font_sub)
tsw = bbox_s[2] - bbox_s[0]
draw.text((cx - tsw // 2, cy + 112), sub, fill=(0, 217, 255), font=font_sub)

# Corner HUD accents
draw.text((30, 45), "[VCC_NODE: SECURE // LINUX WORKSTATION]", fill=(130, 148, 140), font=font_hud)
draw.text((30, 65), "IP_STACK: ACTIVE | DISPLAY: X11 | DESKTOP: XFCE4 CYBERPUNK", fill=(57, 255, 136), font=font_hud)

draw.text((W - 380, 45), "SYS_ARCH: x86_64 // KERNEL 6.x ROLLING", fill=(130, 148, 140), font=font_hud)
draw.text((W - 380, 65), "DEFENSE: MONITORED // ETHEREUM & WEB3 DEV", fill=(0, 217, 255), font=font_hud)

# Save to assets and Pictures
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
PIC_FILE.parent.mkdir(parents=True, exist_ok=True)

im.save(OUT_FILE)
im.save(PIC_FILE)
print(f"[OK] Wallpaper successfully generated: {OUT_FILE} and {PIC_FILE}")


if __name__ == "__main__":
    pass

