# Configuration Guide — Victor Command Center & XFCE Desktop

## Overview

The entire Kali Linux desktop is managed through a unified configuration model:
1. **User Configuration**: `~/.config/victor-command-center/config.json`
2. **Native XFCE Desktop Settings**:
   - Panels: `~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml`
   - Window Manager: `~/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml`
   - GTK / Icons / Fonts: `~/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml`
   - Desktop & Wallpaper: `~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml`
   - GTK3 Application Styling: `~/.config/gtk-3.0/gtk.css`
   - Conky Desktop Widget: `~/.config/conky/victor-cyberpunk.conkyrc`
   - QTerminal Scheme: `~/.local/share/qtermwidget6/color-schemes/Victor-Cyberpunk.colorscheme`

---

## Design System Palette

| Token | Hex Value | Role |
| :--- | :--- | :--- |
| **Primary Background** | `#080C0B` | Windows, panels, dialogs, desktop base |
| **Secondary Background** | `#111820` | Headers, dock container, card sub-boxes |
| **Primary Accent** | `#39FF88` | Active borders, titlebars, clock, selection highlights |
| **Secondary Accent** | `#00D9FF` | Status indicators, focus rings, network gauges |
| **Primary Text** | `#D6E5DF` | Main interface labels, body text |
| **Muted Text** | `#82948C` | Subtitles, disabled states, inactive window titles |

---

## Complete Desktop Presets

### 1. Cyberpunk Green (Default)
- **Primary Accent**: `#39FF88` (Neon Green)
- **Secondary Accent**: `#00D9FF` (Electric Cyan)
- **GTK Theme**: `Kali-Dark` + Custom Green `#39FF88` GTK3 CSS
- **Window Manager**: `Victor-Cyberpunk` (Matte black titlebars with neon green bottom borders)
- **Icon Theme**: `Flat-Remix-Green-Dark`
- **Wallpaper**: `/home/alpha/Pictures/victor-cyberpunk-wallpaper.png`
- **Conky Widget**: Green `#39FF88` / Cyan `#00D9FF` graphs

### 2. Cyberpunk Blue
- **Primary Accent**: `#00D2FF` (Electric Cyan)
- **Secondary Accent**: `#3B82F6` (Electric Blue)
- **GTK Theme**: `Kali-Dark` + Custom Cyan GTK3 CSS
- **Window Manager**: `Kali-Dark`
- **Icon Theme**: `Flat-Remix-Blue-Dark`
- **Wallpaper**: `/usr/share/backgrounds/kali/kali-net-16x9.jpg`

### 3. Matrix Dark
- **Primary Accent**: `#00FF41` (Matrix Green)
- **Secondary Accent**: `#008F11` (Forest Green)
- **GTK Theme**: `Kali-Dark` + Matrix GTK3 CSS
- **Window Manager**: `Victor-Cyberpunk`
- **Icon Theme**: `Flat-Remix-Green-Dark`
- **Wallpaper**: `/usr/share/backgrounds/kali/kali-glitch-16x9.jpg`

### 4. Minimal Hacker
- **Primary Accent**: `#00F0FF` (Neon Cyan)
- **Secondary Accent**: `#FF007F` (Neon Pink)
- **GTK Theme**: `Kali-Dark` + Cyberpunk Synth GTK3 CSS
- **Window Manager**: `Kali-Teal-Dark`
- **Icon Theme**: `Flat-Remix-Teal-Dark`
- **Wallpaper**: `/usr/share/backgrounds/kali/kali-cubes2-16x9.jpg`

---

## Desktop Components Configuration

### Top Navigation Panel (Panel 1)
- Position: Top (`p=6`), 100% width, height 32px
- Styled via GTK3 CSS with dark transparent background (`rgba(8,12,11,0.94)`) and a glowing neon green bottom line (`#39FF88`).
- Integrated Plugins:
  - `whiskermenu`: Branded with Victor's cyberpunk icon and title `VICTOR // VCC`.
  - `places`: Quick places / file navigation.
  - `cpugraph`: Real-time neon green/cyan hardware graph.
  - `genmon`: Kali network and VPN monitor script.
  - `systray`, `pulseaudio`, `power-manager-plugin`, `notification-plugin`.
  - `clock`: Styled with `FiraCode Bold 10` displaying date and time.
  - `actions`: Quick session lock / logout.

### Bottom Application Dock (Panel 2)
- Position: Bottom Center (`p=10`), height 44px, rounded pill container.
- Launchers configured:
  1. QTerminal
  2. Thunar File Manager
  3. Chromium Browser
  4. Antigravity IDE
  5. Bruno API Client
  6. Wireshark
  7. Victor Command Center
- Window tasklist: Icon-only flat buttons with neon running indicators.
- Trash plugin: Desktop trash can integrated at the dock tail.

### Desktop System Telemetry (Conky)
- Integrated into the desktop root window.
- Configured in `~/.config/conky/victor-cyberpunk.conkyrc`.
- Automatically launched on desktop login via `~/.config/autostart/victor-conky.desktop`.
- Reads real system statistics from Linux kernel `/proc/stat`, `/proc/meminfo`, `/proc/net/dev`, and thermal sensors.
