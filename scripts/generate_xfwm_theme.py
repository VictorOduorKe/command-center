#!/usr/bin/env python3
"""
Generates the custom Victor-Cyberpunk xfwm4 window manager theme.
Matte black titlebars (#080C0B), neon green accents (#39FF88),
electric cyan details (#00D9FF), and futuristic window buttons.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw

THEME_DIR = Path.home() / ".themes" / "Victor-Cyberpunk" / "xfwm4"
THEME_DIR.mkdir(parents=True, exist_ok=True)

# Color constants
C_BG_ACTIVE = (8, 12, 11, 255)         # #080C0B
C_BG_INACTIVE = (17, 24, 32, 255)      # #111820
C_ACCENT_GREEN = (57, 255, 136, 255)   # #39FF88
C_ACCENT_CYAN = (0, 217, 255, 255)     # #00D9FF
C_ACCENT_RED = (255, 51, 102, 255)     # #FF3366
C_MUTED = (130, 148, 140, 255)         # #82948C
C_BORDER_DARK = (22, 36, 32, 255)
C_TRANSPARENT = (0, 0, 0, 0)


def create_titlebar(active: bool) -> Image.Image:
    # 5px width, 31px height
    im = Image.new("RGBA", (5, 31), C_BG_ACTIVE if active else C_BG_INACTIVE)
    draw = ImageDraw.Draw(im)
    if active:
        # Subtle top highlight
        draw.line([(0, 0), (4, 0)], fill=(20, 32, 28, 255))
        # Neon Green bottom border
        draw.line([(0, 29), (4, 29)], fill=C_ACCENT_GREEN)
        draw.line([(0, 30), (4, 30)], fill=(28, 128, 68, 255))
    else:
        draw.line([(0, 30), (4, 30)], fill=C_BORDER_DARK)
    return im


def create_button(btn_type: str, state: str) -> Image.Image:
    # 20x20 button
    im = Image.new("RGBA", (20, 20), C_TRANSPARENT)
    draw = ImageDraw.Draw(im)

    if btn_type == "close":
        color = C_ACCENT_RED if state != "inactive" else C_MUTED
    elif btn_type == "maximize":
        color = C_ACCENT_CYAN if state != "inactive" else C_MUTED
    elif btn_type == "hide":
        color = C_ACCENT_GREEN if state != "inactive" else C_MUTED
    else:
        color = C_MUTED

    if state == "prelight":
        # Filled glowing circle
        draw.ellipse([2, 2, 17, 17], fill=(*color[:3], 60), outline=color, width=1)
    elif state == "pressed":
        draw.ellipse([2, 2, 17, 17], fill=(*color[:3], 140), outline=color, width=1)
    else:
        draw.ellipse([3, 3, 16, 16], outline=color, width=1)

    # Inner glyph
    cx, cy = 9, 9
    if btn_type == "close":
        draw.line([(cx - 3, cy - 3), (cx + 3, cy + 3)], fill=color, width=1)
        draw.line([(cx + 3, cy - 3), (cx - 3, cy + 3)], fill=color, width=1)
    elif btn_type == "maximize":
        draw.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], outline=color, width=1)
    elif btn_type == "hide":
        draw.line([(cx - 3, cy + 1), (cx + 3, cy + 1)], fill=color, width=1)
    elif btn_type == "menu":
        draw.rectangle([cx - 3, cy - 2, cx + 3, cy + 2], outline=color, width=1)
    elif btn_type == "shade" or btn_type == "stick":
        draw.line([(cx - 2, cy - 2), (cx + 2, cy - 2)], fill=color, width=1)

    return im


def create_borders():
    # Left & Right borders (4x16)
    for active, prefix in [(True, "active"), (False, "inactive")]:
        color = C_BG_ACTIVE if active else C_BG_INACTIVE
        border_col = C_ACCENT_GREEN if active else C_BORDER_DARK

        # Left border
        im_l = Image.new("RGBA", (4, 16), color)
        d_l = ImageDraw.Draw(im_l)
        d_l.line([(0, 0), (0, 15)], fill=border_col)
        im_l.save(THEME_DIR / f"left-{prefix}.png")

        # Right border
        im_r = Image.new("RGBA", (4, 16), color)
        d_r = ImageDraw.Draw(im_r)
        d_r.line([(3, 0), (3, 15)], fill=border_col)
        im_r.save(THEME_DIR / f"right-{prefix}.png")

        # Bottom border (16x4)
        im_b = Image.new("RGBA", (16, 4), color)
        d_b = ImageDraw.Draw(im_b)
        d_b.line([(0, 3), (15, 3)], fill=border_col)
        im_b.save(THEME_DIR / f"bottom-{prefix}.png")

        # Bottom corners
        im_bl = Image.new("RGBA", (4, 4), color)
        ImageDraw.Draw(im_bl).point([(0, 3)], fill=border_col)
        im_bl.save(THEME_DIR / f"bottom-left-{prefix}.png")

        im_br = Image.new("RGBA", (4, 4), color)
        ImageDraw.Draw(im_br).point([(3, 3)], fill=border_col)
        im_br.save(THEME_DIR / f"bottom-right-{prefix}.png")

        # Top corners
        im_tl = Image.new("RGBA", (4, 31), color)
        im_tl.save(THEME_DIR / f"top-left-{prefix}.png")

        im_tr = Image.new("RGBA", (4, 31), color)
        im_tr.save(THEME_DIR / f"top-right-{prefix}.png")


def main():
    print(f"Generating Victor-Cyberpunk xfwm4 theme in {THEME_DIR}...")

    # Titlebars 1..5
    for i in range(1, 6):
        im_act = create_titlebar(True)
        im_inact = create_titlebar(False)
        im_act.save(THEME_DIR / f"title-{i}-active.png")
        im_inact.save(THEME_DIR / f"title-{i}-inactive.png")

    # Buttons
    buttons = ["close", "maximize", "hide", "menu", "shade", "stick"]
    states = ["active", "inactive", "prelight", "pressed"]
    for b in buttons:
        for s in states:
            im = create_button(b, s)
            im.save(THEME_DIR / f"{b}-{s}.png")

    # Borders
    create_borders()

    # themerc configuration
    themerc_content = """# Victor-Cyberpunk xfwm4 Theme
active_text_color=#39FF88
inactive_text_color=#82948C
active_color_1=#080C0B
active_color_2=#111820
inactive_color_1=#111820
inactive_color_2=#080C0B

button_offset=2
button_spacing=4
show_app_icon=true
full_width_title=true
maximized_offset=0
title_horizontal_offset=4
title_shadow_active=false
title_shadow_inactive=false
title_vertical_offset_active=0
title_vertical_offset_inactive=0

shadow_delta_height=3
shadow_delta_width=0
shadow_delta_x=0
shadow_delta_y=-2
shadow_opacity=55
"""
    with open(THEME_DIR / "themerc", "w", encoding="utf-8") as f:
        f.write(themerc_content)

    print("[OK] Victor-Cyberpunk xfwm4 theme successfully generated.")


if __name__ == "__main__":
    main()

