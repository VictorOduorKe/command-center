#!/usr/bin/env python3
"""
Victor Command Center - Dynamic Desktop Integrator
Transforms the real XFCE desktop environment based on the active theme preset or custom user colors:
- GTK3 CSS: dynamically compiles color definitions to ~/.config/gtk-3.0/gtk.css
- Window Manager: configures xfwm4 theme and border accents
- Icon Theme: Flat-Remix-Green-Dark, Flat-Remix-Blue-Dark, Flat-Remix-Teal-Dark
- Wallpaper: applies customized wallpaper per preset
- Panel & Dock: updates XFCE Top Navigation and Bottom Dock
- Desktop Widgets: reloads Conky with matching cyberpunk accent colors
- Real-time live reload of running XFCE desktop session
"""

import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

HOME = Path.home()
VCC_DIR = Path("/home/alpha/victor-command-center")
XFCE_PERCHANNEL_DIR = HOME / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml"
XSETTINGS_XML = XFCE_PERCHANNEL_DIR / "xsettings.xml"
XFWM4_XML = XFCE_PERCHANNEL_DIR / "xfwm4.xml"
DESKTOP_XML = XFCE_PERCHANNEL_DIR / "xfce4-desktop.xml"
PANEL_XML = XFCE_PERCHANNEL_DIR / "xfce4-panel.xml"
GTK_CSS_USER = HOME / ".config" / "gtk-3.0" / "gtk.css"
THEMES_DIR = HOME / ".themes" / "Victor-Cyberpunk"
CONKY_RC = HOME / ".config" / "conky" / "victor-cyberpunk.conkyrc"

ENV = {
    **os.environ,
    "DISPLAY": ":0",
    "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus"
}

PRESET_PROFILES: Dict[str, Dict[str, str]] = {
    "Cyberpunk Green": {
        "primary_bg": "#080C0B",
        "secondary_bg": "#111820",
        "primary_accent": "#39FF88",
        "secondary_accent": "#00D9FF",
        "text": "#D6E5DF",
        "muted": "#82948C",
        "gtk_base": "Kali-Dark",
        "icon_theme": "Flat-Remix-Green-Dark",
        "xfwm_theme": "Victor-Cyberpunk",
        "wallpaper": str(HOME / "Pictures" / "victor-cyberpunk-wallpaper.png")
    },
    "Cyberpunk Blue": {
        "primary_bg": "#060A14",
        "secondary_bg": "#0F172A",
        "primary_accent": "#00D2FF",
        "secondary_accent": "#3B82F6",
        "text": "#E2E8F0",
        "muted": "#64748B",
        "gtk_base": "Kali-Dark",
        "icon_theme": "Flat-Remix-Blue-Dark",
        "xfwm_theme": "Kali-Dark",
        "wallpaper": "/usr/share/backgrounds/kali/kali-net-16x9.jpg"
    },
    "Matrix Dark": {
        "primary_bg": "#040804",
        "secondary_bg": "#0A140A",
        "primary_accent": "#00FF41",
        "secondary_accent": "#008F11",
        "text": "#C4F9C4",
        "muted": "#557A55",
        "gtk_base": "Kali-Dark",
        "icon_theme": "Flat-Remix-Green-Dark",
        "xfwm_theme": "Victor-Cyberpunk",
        "wallpaper": "/usr/share/backgrounds/kali/kali-glitch-16x9.jpg"
    },
    "Minimal Hacker": {
        "primary_bg": "#0E0E11",
        "secondary_bg": "#18181F",
        "primary_accent": "#00F0FF",
        "secondary_accent": "#FF007F",
        "text": "#F1F1F1",
        "muted": "#797985",
        "gtk_base": "Kali-Dark",
        "icon_theme": "Flat-Remix-Teal-Dark",
        "xfwm_theme": "Kali-Teal-Dark",
        "wallpaper": "/usr/share/backgrounds/kali/kali-cubes2-16x9.jpg"
    }
}


def compile_gtk_css(profile: Dict[str, str]) -> str:
    """Generate dynamic GTK3 CSS matching exact theme colors."""
    bg = profile.get("primary_bg", "#080C0B")
    sub_bg = profile.get("secondary_bg", "#111820")
    accent = profile.get("primary_accent", "#39FF88")
    cyan = profile.get("secondary_accent", "#00D9FF")
    text = profile.get("text", "#D6E5DF")
    muted = profile.get("muted", "#82948C")

    # Read base template or generate
    base_file = VCC_DIR / "assets" / "cyberpunk-gtk.css"
    if base_file.exists():
        with open(base_file, "r", encoding="utf-8") as f:
            css = f.read()
        css = re.sub(r'@define-color theme_bg_color #[0-9a-fA-F]+;', f'@define-color theme_bg_color {bg};', css)
        css = re.sub(r'@define-color theme_base_color #[0-9a-fA-F]+;', f'@define-color theme_base_color {bg};', css)
        css = re.sub(r'@define-color theme_selected_bg_color #[0-9a-fA-F]+;', f'@define-color theme_selected_bg_color {accent};', css)
        css = re.sub(r'@define-color theme_fg_color #[0-9a-fA-F]+;', f'@define-color theme_fg_color {text};', css)
        css = re.sub(r'@define-color theme_unfocused_bg_color #[0-9a-fA-F]+;', f'@define-color theme_unfocused_bg_color {sub_bg};', css)
        return css
    return ""


def apply_full_desktop_theme(preset_name: str = "Cyberpunk Green", custom_colors: Dict[str, str] = None) -> bool:
    """Applies the complete desktop theme directly to XFCE and active session."""
    prof = PRESET_PROFILES.get(preset_name, PRESET_PROFILES["Cyberpunk Green"]).copy()
    if custom_colors:
        prof.update(custom_colors)

    print(f"\n=======================================================")
    print(f" APPLYING REAL DESKTOP THEME: {preset_name}")
    print(f"=======================================================")

    # 1. Update GTK CSS
    css_content = compile_gtk_css(prof)
    if css_content:
        GTK_CSS_USER.parent.mkdir(parents=True, exist_ok=True)
        with open(GTK_CSS_USER, "w", encoding="utf-8") as f:
            f.write(css_content)
        theme_gtk_dir = THEMES_DIR / "gtk-3.0"
        theme_gtk_dir.mkdir(parents=True, exist_ok=True)
        with open(theme_gtk_dir / "gtk.css", "w", encoding="utf-8") as f:
            f.write(css_content)
        print("[OK] Real-time GTK CSS updated.")

    # 2. Update xsettings.xml (Theme, Icons, Font)
    if XSETTINGS_XML.exists():
        with open(XSETTINGS_XML, "r", encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'(<property name="ThemeName" type="string" value=")[^"]*("/>)', rf'\g<1>{prof["gtk_base"]}\2', c)
        c = re.sub(r'(<property name="IconThemeName" type="string" value=")[^"]*("/>)', rf'\g<1>{prof["icon_theme"]}\2', c)
        with open(XSETTINGS_XML, "w", encoding="utf-8") as f:
            f.write(c)

    # Apply live xsettings properties
    for prop, val in [
        ("/Net/ThemeName", prof["gtk_base"]),
        ("/Net/IconThemeName", prof["icon_theme"]),
        ("/Gtk/FontName", "FiraCode 10"),
        ("/Gtk/MonospaceFontName", "FiraCode 10")
    ]:
        try:
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", prop, "-s", val], env=ENV, check=False)
        except Exception:
            pass
    print(f"[OK] Live GTK Base set to {prof['gtk_base']}, Icons set to {prof['icon_theme']}")

    # 3. Update xfwm4 Window Manager
    if XFWM4_XML.exists():
        with open(XFWM4_XML, "r", encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'(<property name="theme" type="string" value=")[^"]*("/>)', rf'\g<1>{prof["xfwm_theme"]}\2', c)
        with open(XFWM4_XML, "w", encoding="utf-8") as f:
            f.write(c)
    try:
        subprocess.run(["xfconf-query", "-c", "xfwm4", "-p", "/general/theme", "-s", prof["xfwm_theme"]], env=ENV, check=False)
        print(f"[OK] Live xfwm4 Window Manager theme set to {prof['xfwm_theme']}")
    except Exception:
        pass

    # 4. Update Desktop Wallpaper
    wp_path = prof["wallpaper"]
    if os.path.exists(wp_path) and DESKTOP_XML.exists():
        with open(DESKTOP_XML, "r", encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'(<property name="image-path" type="string" value=")[^"]*("/>)', rf'\g<1>{wp_path}\2', c)
        c = re.sub(r'(<property name="last-image" type="string" value=")[^"]*("/>)', rf'\g<1>{wp_path}\2', c)
        with open(DESKTOP_XML, "w", encoding="utf-8") as f:
            f.write(c)
        try:
            subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitorLVDS-1/workspace0/last-image", "-s", wp_path], env=ENV, check=False)
            subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-path", "-s", wp_path], env=ENV, check=False)
            subprocess.run(["xfdesktop", "--reload"], env=ENV, timeout=3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[OK] Desktop wallpaper set to {wp_path}")
        except Exception:
            pass

    # 5. Restart XFCE Panel to refresh top panel and dock styling
    try:
        subprocess.run(["xfce4-panel", "--restart"], env=ENV, timeout=3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[OK] XFCE Panels restarted and restyled.")
    except Exception:
        pass

    # 6. Update Conky colors & reload
    update_conky_colors(prof["primary_accent"], prof["secondary_accent"])

    print("\n[SUCCESS] Actual Kali Linux Desktop visibly transformed.")
    return True


def update_conky_colors(accent_green: str, accent_cyan: str):
    """Update conky accent colors and trigger reload."""
    if CONKY_RC.exists():
        with open(CONKY_RC, "r", encoding="utf-8") as f:
            text = f.read()
        text = re.sub(r"color1 = '#[0-9a-fA-F]+'", f"color1 = '{accent_green}'", text)
        text = re.sub(r"color2 = '#[0-9a-fA-F]+'", f"color2 = '{accent_cyan}'", text)
        with open(CONKY_RC, "w", encoding="utf-8") as f:
            f.write(text)

        # Trigger Conky reload via SIGUSR1 or restart
        subprocess.run(["pkill", "-x", "conky"], check=False)
        time.sleep(0.3)
        conky_bin = HOME / ".local" / "bin" / "conky"
        if conky_bin.exists():
            subprocess.Popen([str(conky_bin), "-c", str(CONKY_RC), "-d"], env=ENV, start_new_session=True)
            print("[OK] Conky desktop widget reloaded with new accent colors.")


if __name__ == "__main__":
    p_name = sys.argv[1] if len(sys.argv) > 1 else "Cyberpunk Green"
    apply_full_desktop_theme(p_name)
