#!/usr/bin/env python3
"""
Victor Command Center - Complete XFCE Desktop Transformation Engine
Transforms the actual Kali Linux XFCE desktop environment:
- Top Navigation Panel with Whiskermenu & Victor branding
- Bottom Modern Application Dock
- Custom xfwm4 Window Decorations (Matte black #080C0B, Neon Green #39FF88)
- Complete Cyberpunk GTK3 styling (menus, buttons, panels, toolbars)
- Flat-Remix-Green-Dark icon theme & FiraCode typography
- Custom Cyberpunk Workstation Wallpaper
- Embedded Conky Desktop System Telemetry Widget
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

# Paths
HOME = Path.home()
VCC_DIR = Path("/home/alpha/victor-command-center")
XFCE_PERCHANNEL_DIR = HOME / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml"
PANEL_XML = XFCE_PERCHANNEL_DIR / "xfce4-panel.xml"
XFWM4_XML = XFCE_PERCHANNEL_DIR / "xfwm4.xml"
XSETTINGS_XML = XFCE_PERCHANNEL_DIR / "xsettings.xml"
DESKTOP_XML = XFCE_PERCHANNEL_DIR / "xfce4-desktop.xml"
GTK_CSS_USER = HOME / ".config" / "gtk-3.0" / "gtk.css"
THEMES_DIR = HOME / ".themes" / "Victor-Cyberpunk"
CONKY_RC = HOME / ".config" / "conky" / "victor-cyberpunk.conkyrc"
WALLPAPER_FILE = HOME / "Pictures" / "victor-cyberpunk-wallpaper.png"

ENV = {
    **os.environ,
    "DISPLAY": ":0",
    "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus"
}


def backup_current_configs():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = HOME / ".config" / "victor-command-center" / "backups" / f"desktop_{ts}"
    backup_path.mkdir(parents=True, exist_ok=True)
    for p in XFCE_PERCHANNEL_DIR.glob("*.xml"):
        shutil.copy2(p, backup_path / p.name)
    if GTK_CSS_USER.exists():
        shutil.copy2(GTK_CSS_USER, backup_path / "gtk.css")
    print(f"[OK] Backup snapshot captured in {backup_path}")


def setup_gtk_and_icons():
    print("Applying GTK3 Theme, Icons, and Typography...")
    # 1. Install GTK CSS
    GTK_CSS_USER.parent.mkdir(parents=True, exist_ok=True)
    src_css = VCC_DIR / "assets" / "cyberpunk-gtk.css"
    if src_css.exists():
        shutil.copy2(src_css, GTK_CSS_USER)
        theme_gtk_dir = THEMES_DIR / "gtk-3.0"
        theme_gtk_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_css, theme_gtk_dir / "gtk.css")
        print(f"[OK] Installed GTK CSS to {GTK_CSS_USER} and {theme_gtk_dir}")

    # 2. Update xsettings.xml
    if XSETTINGS_XML.exists():
        with open(XSETTINGS_XML, "r", encoding="utf-8") as f:
            c = f.read()
        # Theme: Kali-Dark (augmented with our GTK3 CSS)
        c = re.sub(r'(<property name="ThemeName" type="string" value=")[^"]*("/>)', r'\g<1>Kali-Dark\2', c)
        # Icons: Flat-Remix-Green-Dark
        c = re.sub(r'(<property name="IconThemeName" type="string" value=")[^"]*("/>)', r'\g<1>Flat-Remix-Green-Dark\2', c)
        # Fonts: FiraCode
        c = re.sub(r'(<property name="FontName" type=")[^"]*(" value=")[^"]*("/>)', r'<property name="FontName" type="string" value="FiraCode 10"/>', c)
        c = re.sub(r'(<property name="MonospaceFontName" type=")[^"]*(" value=")[^"]*("/>)', r'<property name="MonospaceFontName" type="string" value="FiraCode 10"/>', c)
        with open(XSETTINGS_XML, "w", encoding="utf-8") as f:
            f.write(c)
        print("[OK] xsettings.xml configured: Kali-Dark + Flat-Remix-Green-Dark + FiraCode")

    # 3. Live xfconf-query update
    for prop, val in [
        ("/Net/ThemeName", "Kali-Dark"),
        ("/Net/IconThemeName", "Flat-Remix-Green-Dark"),
        ("/Gtk/FontName", "FiraCode 10"),
        ("/Gtk/MonospaceFontName", "FiraCode 10")
    ]:
        try:
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", prop, "-s", val], env=ENV, check=False)
        except Exception:
            pass


def setup_window_manager():
    print("Applying xfwm4 Window Manager decorations...")
    # Generate xfwm4 theme
    gen_script = VCC_DIR / "scripts" / "generate_xfwm_theme.py"
    if gen_script.exists():
        subprocess.run(["python3", str(gen_script)], env=ENV, check=False)

    # Set theme in xfwm4.xml
    if XFWM4_XML.exists():
        with open(XFWM4_XML, "r", encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'(<property name="theme" type="string" value=")[^"]*("/>)', r'\g<1>Victor-Cyberpunk\2', c)
        with open(XFWM4_XML, "w", encoding="utf-8") as f:
            f.write(c)

    try:
        subprocess.run(["xfconf-query", "-c", "xfwm4", "-p", "/general/theme", "-s", "Victor-Cyberpunk"], env=ENV, check=False)
        print("[OK] xfwm4 theme set to Victor-Cyberpunk")
    except Exception:
        pass


def setup_wallpaper():
    print("Applying Custom Cyberpunk Workstation Wallpaper...")
    gen_wp = VCC_DIR / "scripts" / "generate_wallpaper.py"
    if gen_wp.exists():
        subprocess.run(["python3", str(gen_wp)], env=ENV, check=False)

    wp_str = str(WALLPAPER_FILE)
    if DESKTOP_XML.exists():
        with open(DESKTOP_XML, "r", encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'(<property name="image-path" type="string" value=")[^"]*("/>)', rf'\g<1>{wp_str}\2', c)
        c = re.sub(r'(<property name="last-image" type="string" value=")[^"]*("/>)', rf'\g<1>{wp_str}\2', c)
        with open(DESKTOP_XML, "w", encoding="utf-8") as f:
            f.write(c)

    # Apply via xfconf-query to active monitorLVDS-1
    try:
        subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitorLVDS-1/workspace0/last-image", "-s", wp_str], env=ENV, check=False)
        subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-path", "-s", wp_str], env=ENV, check=False)
        print(f"[OK] Desktop wallpaper set to {wp_str}")
    except Exception:
        pass


def setup_panels():
    print("Transforming Top Navigation Panel and Bottom Application Dock...")
    # 1. Setup dock launcher directories
    launchers = [
        (40, "/usr/share/applications/qterminal.desktop"),
        (41, "/usr/share/applications/thunar.desktop"),
        (42, "/usr/share/applications/chromium.desktop"),
        (43, "/usr/share/applications/antigravity.desktop"),
        (44, "/usr/share/applications/bruno.desktop"),
        (45, "/usr/share/applications/org.wireshark.Wireshark.desktop"),
        (46, str(HOME / ".local" / "share" / "applications" / "victor-command-center.desktop")),
    ]
    for lid, src in launchers:
        ldir = HOME / ".config" / "xfce4" / "panel" / f"launcher-{lid}"
        ldir.mkdir(parents=True, exist_ok=True)
        if os.path.exists(src):
            shutil.copy2(src, ldir / Path(src).name)

    # 2. Render complete cyberpunk xfce4-panel.xml
    svg_icon = str(VCC_DIR / "assets" / "victor-command-center.svg")
    panel_xml_content = f"""<?xml version="1.1" encoding="UTF-8"?>

<channel name="xfce4-panel" version="1.0">
  <property name="configver" type="int" value="2"/>
  <property name="panels" type="array">
    <value type="int" value="1"/>
    <value type="int" value="2"/>
    <property name="panel-1" type="empty">
      <property name="background-rgba" type="array">
        <value type="double" value="0.03137"/>
        <value type="double" value="0.04705"/>
        <value type="double" value="0.04313"/>
        <value type="double" value="0.94"/>
      </property>
      <property name="background-style" type="uint" value="1"/>
      <property name="length" type="uint" value="100"/>
      <property name="plugin-ids" type="array">
        <value type="int" value="29"/>
        <value type="int" value="25"/>
        <value type="int" value="26"/>
        <value type="int" value="12"/>
        <value type="int" value="13"/>
        <value type="int" value="15"/>
        <value type="int" value="14"/>
        <value type="int" value="16"/>
        <value type="int" value="18"/>
        <value type="int" value="17"/>
        <value type="int" value="2"/>
        <value type="int" value="22"/>
      </property>
      <property name="position" type="string" value="p=6;x=0;y=0"/>
      <property name="position-locked" type="bool" value="true"/>
      <property name="size" type="uint" value="32"/>
    </property>
    <property name="panel-2" type="empty">
      <property name="background-rgba" type="array">
        <value type="double" value="0.0666"/>
        <value type="double" value="0.0941"/>
        <value type="double" value="0.1254"/>
        <value type="double" value="0.92"/>
      </property>
      <property name="background-style" type="uint" value="1"/>
      <property name="length" type="double" value="1"/>
      <property name="length-adjust" type="bool" value="true"/>
      <property name="plugin-ids" type="array">
        <value type="int" value="24"/>
        <value type="int" value="40"/>
        <value type="int" value="41"/>
        <value type="int" value="42"/>
        <value type="int" value="43"/>
        <value type="int" value="44"/>
        <value type="int" value="45"/>
        <value type="int" value="46"/>
        <value type="int" value="34"/>
        <value type="int" value="30"/>
        <value type="int" value="28"/>
      </property>
      <property name="position" type="string" value="p=10;x=0;y=0"/>
      <property name="position-locked" type="bool" value="true"/>
      <property name="size" type="uint" value="44"/>
    </property>
  </property>
  <property name="plugins" type="empty">
    <!-- Top Navigation Panel Plugins -->
    <property name="plugin-29" type="string" value="whiskermenu">
      <property name="button-icon" type="string" value="{svg_icon}"/>
      <property name="button-title" type="string" value=" VICTOR // VCC "/>
      <property name="show-button-title" type="bool" value="true"/>
      <property name="show-button-icon" type="bool" value="true"/>
    </property>
    <property name="plugin-25" type="string" value="places">
      <property name="show-button-type" type="int" value="1"/>
    </property>
    <property name="plugin-26" type="string" value="separator">
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-12" type="string" value="separator">
      <property name="expand" type="bool" value="true"/>
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-13" type="string" value="cpugraph">
      <property name="background" type="array">
        <value type="double" value="0.031"/>
        <value type="double" value="0.047"/>
        <value type="double" value="0.043"/>
        <value type="double" value="0"/>
      </property>
      <property name="bars" type="int" value="1"/>
      <property name="bars-color" type="array">
        <value type="double" value="0.2235"/>
        <value type="double" value="1.0"/>
        <value type="double" value="0.5333"/>
        <value type="double" value="1"/>
      </property>
      <property name="border" type="int" value="0"/>
      <property name="color-mode" type="int" value="1"/>
      <property name="foreground-1" type="array">
        <value type="double" value="0.2235"/>
        <value type="double" value="1.0"/>
        <value type="double" value="0.5333"/>
        <value type="double" value="1"/>
      </property>
      <property name="foreground-2" type="array">
        <value type="double" value="0.0"/>
        <value type="double" value="0.85"/>
        <value type="double" value="1.0"/>
        <value type="double" value="1"/>
      </property>
      <property name="foreground-3" type="array">
        <value type="double" value="0.0"/>
        <value type="double" value="0.45"/>
        <value type="double" value="0.9"/>
        <value type="double" value="1"/>
      </property>
    </property>
    <property name="plugin-15" type="string" value="genmon">
      <property name="command" type="string" value="/usr/share/kali-themes/xfce4-panel-genmon-vpnip.sh"/>
      <property name="enable-single-row" type="bool" value="true"/>
      <property name="font" type="string" value="FiraCode 9"/>
      <property name="text" type="string" value="(genmon)"/>
      <property name="update-period" type="int" value="1000"/>
    </property>
    <property name="plugin-14" type="string" value="systray"/>
    <property name="plugin-16" type="string" value="pulseaudio">
      <property name="enable-keyboard-shortcuts" type="bool" value="true"/>
    </property>
    <property name="plugin-18" type="string" value="power-manager-plugin"/>
    <property name="plugin-17" type="string" value="notification-plugin"/>
    <property name="plugin-2" type="string" value="clock">
      <property name="digital-date-font" type="string" value="FiraCode Bold 10"/>
      <property name="digital-date-format" type="string" value="%a %b %d  %l:%M %p"/>
      <property name="digital-layout" type="uint" value="2"/>
      <property name="digital-time-format" type="string" value="%a %b %d  %l:%M %p"/>
    </property>
    <property name="plugin-22" type="string" value="actions">
      <property name="appearance" type="uint" value="0"/>
    </property>

    <!-- Bottom Dock Plugins -->
    <property name="plugin-24" type="string" value="showdesktop"/>
    <property name="plugin-40" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="qterminal.desktop"/>
      </property>
    </property>
    <property name="plugin-41" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="thunar.desktop"/>
      </property>
    </property>
    <property name="plugin-42" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="chromium.desktop"/>
      </property>
    </property>
    <property name="plugin-43" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="antigravity.desktop"/>
      </property>
    </property>
    <property name="plugin-44" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="bruno.desktop"/>
      </property>
    </property>
    <property name="plugin-45" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="org.wireshark.Wireshark.desktop"/>
      </property>
    </property>
    <property name="plugin-46" type="string" value="launcher">
      <property name="items" type="array">
        <value type="string" value="victor-command-center.desktop"/>
      </property>
    </property>
    <property name="plugin-34" type="string" value="separator">
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-30" type="string" value="tasklist">
      <property name="flat-buttons" type="bool" value="true"/>
      <property name="show-handle" type="bool" value="false"/>
      <property name="show-labels" type="bool" value="false"/>
      <property name="grouping" type="uint" value="1"/>
      <property name="switch-workspace-on-unminimize" type="bool" value="true"/>
    </property>
    <property name="plugin-28" type="string" value="thunar-tpa"/>
  </property>
</channel>
"""
    with open(PANEL_XML, "w", encoding="utf-8") as f:
        f.write(panel_xml_content)
    print("[OK] xfce4-panel.xml written: Top Navigation Panel + Bottom Centered Application Dock")


def setup_conky_widget():
    print("Configuring and Starting Cyberpunk Conky Desktop Widget...")
    conky_src = VCC_DIR / "assets" / "victor-cyberpunk.conkyrc"
    CONKY_RC.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(conky_src, CONKY_RC)

    # Kill any existing conky process and restart
    subprocess.run(["pkill", "-x", "conky"], check=False)
    time.sleep(0.5)

    conky_bin = HOME / ".local" / "bin" / "conky"
    if conky_bin.exists():
        subprocess.Popen([str(conky_bin), "-c", str(CONKY_RC), "-d"], env=ENV, start_new_session=True)
        print("[OK] Conky desktop widget launched.")


def reload_xfce_desktop():
    print("Reloading live XFCE Desktop session...")
    # 1. Update theme live via xfconf
    subprocess.run(["xfconf-query", "-c", "xfwm4", "-p", "/general/theme", "-s", "Victor-Cyberpunk"], env=ENV, check=False)
    subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "-s", "Kali-Dark"], env=ENV, check=False)
    subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", "-s", "Flat-Remix-Green-Dark"], env=ENV, check=False)

    # 2. Restart xfce4-panel to apply new layout, whiskermenu & dock
    try:
        subprocess.run(["xfce4-panel", "--restart"], env=ENV, timeout=3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # 3. Reload desktop wallpaper
    try:
        subprocess.run(["xfdesktop", "--reload"], env=ENV, timeout=3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    print("[OK] XFCE desktop components reloaded.")


def main():
    print("=" * 70)
    print(" STARTING COMPLETE KALI LINUX XFCE DESKTOP TRANSFORMATION ")
    print("=" * 70)
    backup_current_configs()
    setup_gtk_and_icons()
    setup_window_manager()
    setup_wallpaper()
    setup_panels()
    setup_conky_widget()
    reload_xfce_desktop()
    print("=" * 70)
    print(" [SUCCESS] ACTUAL KALI LINUX XFCE DESKTOP FULLY TRANSFORMED ")
    print("=" * 70)


if __name__ == "__main__":
    main()
