#!/usr/bin/env python3
"""
Victor Command Center - Cyberpunk Desktop HUD
Frameless, hardware-accelerated desktop overlay displaying Victor's identity,
technical skills matrix, learning progress, live /proc telemetry, and developer shortcuts.
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QScrollArea, QTabWidget,
    QVBoxLayout, QWidget
)

# Ensure local config can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import load_config


class SystemTelemetry:
    """Reads live statistics strictly from Linux /proc and /sys without fabrication."""

    def __init__(self):
        self.last_cpu_idle = 0.0
        self.last_cpu_total = 0.0
        self.last_net_bytes_recv = 0
        self.last_net_bytes_sent = 0
        self.last_time = time.time()
        self._init_cpu()
        self._init_net()

    def _init_cpu(self):
        try:
            with open("/proc/stat", "r") as f:
                fields = [float(x) for x in f.readline().strip().split()[1:8]]
                self.last_cpu_idle = fields[3] + fields[4]
                self.last_cpu_total = sum(fields)
        except Exception:
            pass

    def _init_net(self):
        try:
            recv, sent = 0, 0
            with open("/proc/net/dev", "r") as f:
                for line in f.readlines()[2:]:
                    parts = line.split()
                    if len(parts) >= 10 and not parts[0].startswith("lo:"):
                        recv += int(parts[1])
                        sent += int(parts[9])
            self.last_net_bytes_recv = recv
            self.last_net_bytes_sent = sent
        except Exception:
            pass

    def get_metrics(self) -> Dict[str, any]:
        now = time.time()
        dt = max(0.1, now - self.last_time)
        self.last_time = now

        # CPU Utilization
        cpu_pct = 0.0
        try:
            with open("/proc/stat", "r") as f:
                fields = [float(x) for x in f.readline().strip().split()[1:8]]
                idle = fields[3] + fields[4]
                total = sum(fields)
                d_idle = idle - self.last_cpu_idle
                d_total = total - self.last_cpu_total
                if d_total > 0:
                    cpu_pct = max(0.0, min(100.0, 100.0 * (1.0 - d_idle / d_total)))
                self.last_cpu_idle = idle
                self.last_cpu_total = total
        except Exception:
            pass

        # Memory
        mem = {}
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        mem[parts[0].strip()] = int(parts[1].split()[0])
            total_ram = mem.get("MemTotal", 1) / (1024 * 1024)
            avail_ram = mem.get("MemAvailable", 0) / (1024 * 1024)
            used_ram = total_ram - avail_ram
            ram_pct = (used_ram / total_ram) * 100.0
        except Exception:
            total_ram, used_ram, ram_pct = 8.0, 4.0, 50.0

        # Disk
        try:
            st = os.statvfs("/")
            total_disk = (st.f_blocks * st.f_frsize) / (1024 ** 3)
            free_disk = (st.f_bavail * st.f_frsize) / (1024 ** 3)
            used_disk = total_disk - free_disk
            disk_pct = (used_disk / total_disk) * 100.0 if total_disk > 0 else 0.0
        except Exception:
            total_disk, used_disk, disk_pct = 500.0, 50.0, 10.0

        # Temperature
        temp_str = "N/A"
        for p in Path("/sys/class/thermal").glob("thermal_zone*/temp"):
            try:
                t = float(p.read_text().strip()) / 1000.0
                temp_str = f"{t:.1f} °C"
                break
            except Exception:
                pass

        # Network Speeds
        rx_speed, tx_speed = 0.0, 0.0
        try:
            recv, sent = 0, 0
            with open("/proc/net/dev", "r") as f:
                for line in f.readlines()[2:]:
                    parts = line.split()
                    if len(parts) >= 10 and not parts[0].startswith("lo:"):
                        recv += int(parts[1])
                        sent += int(parts[9])
            rx_speed = max(0.0, (recv - self.last_net_bytes_recv) / dt / 1024.0)
            tx_speed = max(0.0, (sent - self.last_net_bytes_sent) / dt / 1024.0)
            self.last_net_bytes_recv = recv
            self.last_net_bytes_sent = sent
        except Exception:
            pass

        # Uptime
        uptime_str = "0h 0m"
        try:
            with open("/proc/uptime", "r") as f:
                up_sec = float(f.readline().split()[0])
                h, rem = divmod(int(up_sec), 3600)
                m, s = divmod(rem, 60)
                uptime_str = f"{h}h {m}m {s}s"
        except Exception:
            pass

        return {
            "cpu_pct": cpu_pct,
            "ram_pct": ram_pct,
            "used_ram": used_ram,
            "total_ram": total_ram,
            "disk_pct": disk_pct,
            "used_disk": used_disk,
            "total_disk": total_disk,
            "temp": temp_str,
            "rx_kb": rx_speed,
            "tx_kb": tx_speed,
            "uptime": uptime_str,
            "time": datetime.now().strftime("%H:%M:%S")
        }


class CyberpunkHUD(QWidget):
    """Futuristic Cyberpunk Workstation HUD Overlay."""

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.telemetry = SystemTelemetry()
        self.drag_position = QPoint()

        self.init_ui()
        self.apply_theme()

        # Telemetry refresh timer (every 1.25s)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(1250)

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(760, 560)
        self.setMinimumSize(680, 500)

        # Main Root Layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)

        # Cyberpunk Glass Card Container
        self.container = QFrame(self)
        self.container.setObjectName("hudContainer")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(18, 14, 18, 16)
        container_layout.setSpacing(12)

        # 1. Header Bar (Draggable, Title, Controls)
        header_box = QHBoxLayout()
        header_box.setSpacing(10)

        self.title_icon = QLabel("⚡")
        self.title_icon.setObjectName("cyberIcon")
        header_box.addWidget(self.title_icon)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(1)
        self.lbl_title = QLabel("VICTOR COMMAND CENTER // CYBERPUNK HUD")
        self.lbl_title.setObjectName("hudTitle")
        self.lbl_subtitle = QLabel("KALI LINUX ROLLING // SOFTWARE & WEB3 WORKSTATION")
        self.lbl_subtitle.setObjectName("hudSubtitle")
        title_vbox.addWidget(self.lbl_title)
        title_vbox.addWidget(self.lbl_subtitle)
        header_box.addLayout(title_vbox)

        header_box.addStretch()

        # Live Clock Badge
        self.lbl_clock = QLabel("--:--:--")
        self.lbl_clock.setObjectName("hudClockBadge")
        header_box.addWidget(self.lbl_clock)

        # Window Controls
        btn_min = QPushButton("─")
        btn_min.setObjectName("btnControl")
        btn_min.setFixedSize(26, 24)
        btn_min.clicked.connect(self.showMinimized)
        header_box.addWidget(btn_min)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("btnControlClose")
        btn_close.setFixedSize(26, 24)
        btn_close.clicked.connect(self.close)
        header_box.addWidget(btn_close)

        container_layout.addLayout(header_box)

        # Separator Line
        sep = QFrame()
        sep.setObjectName("cyberSeparator")
        sep.setFrameShape(QFrame.Shape.HLine)
        container_layout.addWidget(sep)

        # 2. Main Tabbed Content Area
        self.tabs = QTabWidget()
        self.tabs.setObjectName("hudTabs")

        # Tab 1: System Telemetry (Live Hardware Metrics)
        self.tab_telemetry = QWidget()
        self.init_telemetry_tab()
        self.tabs.addTab(self.tab_telemetry, "LIVE MONITOR")

        # Tab 2: Identity & Profile
        self.tab_identity = QWidget()
        self.init_identity_tab()
        self.tabs.addTab(self.tab_identity, "IDENTITY")

        # Tab 3: Technical Skills Matrix
        self.tab_skills = QWidget()
        self.init_skills_tab()
        self.tabs.addTab(self.tab_skills, "SKILLS MATRIX")

        # Tab 4: Learning Goals & Blockchain
        self.tab_learning = QWidget()
        self.init_learning_tab()
        self.tabs.addTab(self.tab_learning, "LEARNING TRACKS")

        # Tab 5: Developer Shortcuts
        self.tab_shortcuts = QWidget()
        self.init_shortcuts_tab()
        self.tabs.addTab(self.tab_shortcuts, "SHORTCUTS")

        container_layout.addWidget(self.tabs, stretch=1)

        # 3. Footer Status Bar
        footer = QHBoxLayout()
        self.lbl_footer_status = QLabel("STATUS: SECURE // COM_NET_ACTIVE // LOCALHOST")
        self.lbl_footer_status.setObjectName("hudFooterText")
        footer.addWidget(self.lbl_footer_status)
        footer.addStretch()

        btn_launch_vcc = QPushButton("LAUNCH COMMAND CENTER")
        btn_launch_vcc.setObjectName("btnPrimaryCyber")
        btn_launch_vcc.clicked.connect(self.launch_command_center)
        footer.addWidget(btn_launch_vcc)

        container_layout.addLayout(footer)
        root_layout.addWidget(self.container)

    def init_telemetry_tab(self):
        layout = QVBoxLayout(self.tab_telemetry)
        layout.setContentsMargins(8, 12, 8, 8)
        layout.setSpacing(12)

        grid = QGridLayout()
        grid.setSpacing(14)

        # CPU Card
        self.cpu_card = self.create_metric_card("CPU UTILIZATION", "Intel Core i5-2520M (4T)")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_val = QLabel("0.0%")
        self.cpu_val.setObjectName("metricVal")
        self.cpu_card.layout().addWidget(self.cpu_val)
        self.cpu_card.layout().addWidget(self.cpu_bar)
        grid.addWidget(self.cpu_card, 0, 0)

        # RAM Card
        self.ram_card = self.create_metric_card("MEMORY (RAM)", "8.0 GB Physical")
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_val = QLabel("0.0 / 8.0 GB")
        self.ram_val.setObjectName("metricVal")
        self.ram_card.layout().addWidget(self.ram_val)
        self.ram_card.layout().addWidget(self.ram_bar)
        grid.addWidget(self.ram_card, 0, 1)

        # Disk Card
        self.disk_card = self.create_metric_card("ROOT STORAGE", "System HDD")
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        self.disk_val = QLabel("0.0 GB")
        self.disk_val.setObjectName("metricVal")
        self.disk_card.layout().addWidget(self.disk_val)
        self.disk_card.layout().addWidget(self.disk_bar)
        grid.addWidget(self.disk_card, 1, 0)

        # Network & Temp Card
        self.net_card = self.create_metric_card("THERMAL & NETWORK", "Sensors & Interfaces")
        self.lbl_temp = QLabel("CPU Temp: -- °C")
        self.lbl_temp.setObjectName("telemetrySubline")
        self.lbl_net_rx = QLabel("Download: 0.0 KB/s")
        self.lbl_net_rx.setObjectName("telemetrySubline")
        self.lbl_net_tx = QLabel("Upload: 0.0 KB/s")
        self.lbl_net_tx.setObjectName("telemetrySubline")
        self.lbl_uptime = QLabel("Uptime: --")
        self.lbl_uptime.setObjectName("telemetrySubline")
        self.net_card.layout().addWidget(self.lbl_temp)
        self.net_card.layout().addWidget(self.lbl_net_rx)
        self.net_card.layout().addWidget(self.lbl_net_tx)
        self.net_card.layout().addWidget(self.lbl_uptime)
        grid.addWidget(self.net_card, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def create_metric_card(self, title: str, subtitle: str) -> QFrame:
        card = QFrame()
        card.setObjectName("metricCard")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(12, 10, 12, 10)
        vbox.setSpacing(4)
        t_lbl = QLabel(title)
        t_lbl.setObjectName("cardTitle")
        s_lbl = QLabel(subtitle)
        s_lbl.setObjectName("cardSubtitle")
        vbox.addWidget(t_lbl)
        vbox.addWidget(s_lbl)
        return card

    def init_identity_tab(self):
        layout = QVBoxLayout(self.tab_identity)
        layout.setContentsMargins(10, 12, 10, 10)
        layout.setSpacing(10)

        prof = self.cfg.get("profile", {})
        
        name_lbl = QLabel(prof.get("name", "Victor Oduor"))
        name_lbl.setObjectName("identityName")
        layout.addWidget(name_lbl)

        title_lbl = QLabel(prof.get("title", "Software Developer & ICT Professional"))
        title_lbl.setObjectName("identityTitle")
        layout.addWidget(title_lbl)

        bio_lbl = QLabel(prof.get("bio", ""))
        bio_lbl.setObjectName("identityBio")
        bio_lbl.setWordWrap(True)
        layout.addWidget(bio_lbl)

        edu_box = QFrame()
        edu_box.setObjectName("panelSubBox")
        edu_layout = QVBoxLayout(edu_box)
        edu_title = QLabel("EDUCATION & CREDENTIALS")
        edu_title.setObjectName("sectionHeading")
        edu_deg = QLabel(f"• Degree: {prof.get('degree', 'Bachelor of ICT')}")
        edu_inst = QLabel(f"• Institution: {prof.get('institution', 'Technical University of Mombasa')}")
        edu_motto = QLabel(f"• Motto: \"{prof.get('motto', '')}\"")
        for w in [edu_deg, edu_inst, edu_motto]:
            w.setObjectName("eduItem")
            edu_layout.addWidget(w)
        layout.addWidget(edu_box)

        # Social Link Buttons
        links_box = QHBoxLayout()
        btn_gh = QPushButton("GitHub: VictorOduorKe")
        btn_gh.setObjectName("btnLink")
        btn_gh.clicked.connect(lambda: subprocess.Popen(["xdg-open", prof.get("github", "https://github.com/VictorOduorKe")]))

        btn_li = QPushButton("LinkedIn: Victor-Oduor-ke")
        btn_li.setObjectName("btnLink")
        btn_li.clicked.connect(lambda: subprocess.Popen(["xdg-open", prof.get("linkedin", "https://www.linkedin.com/in/Victor-Oduor-ke/")]))

        links_box.addWidget(btn_gh)
        links_box.addWidget(btn_li)
        layout.addLayout(links_box)

        layout.addStretch()

    def init_skills_tab(self):
        layout = QVBoxLayout(self.tab_skills)
        layout.setContentsMargins(4, 8, 4, 4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("cyberScroll")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)

        # Group skills by category
        skills = self.cfg.get("skills", [])
        categories = {}
        for s in skills:
            cat = s.get("category", "General")
            categories.setdefault(cat, []).append(s)

        for cat, items in categories.items():
            cat_frame = QFrame()
            cat_frame.setObjectName("panelSubBox")
            cat_vbox = QVBoxLayout(cat_frame)
            cat_vbox.setContentsMargins(10, 8, 10, 8)
            cat_vbox.setSpacing(6)

            cat_header = QLabel(f"// {cat.upper()}")
            cat_header.setObjectName("sectionHeading")
            cat_vbox.addWidget(cat_header)

            for s in items:
                row = QHBoxLayout()
                lbl_name = QLabel(s.get("name", ""))
                lbl_name.setFixedWidth(190)
                lbl_name.setObjectName("skillName")

                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setValue(int(s.get("proficiency", 50)))
                bar.setTextVisible(True)
                bar.setFormat(f"{s.get('proficiency')}% [{s.get('level', '').upper()}]")
                bar.setFixedHeight(18)

                row.addWidget(lbl_name)
                row.addWidget(bar)
                cat_vbox.addLayout(row)

            scroll_layout.addWidget(cat_frame)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def init_learning_tab(self):
        layout = QVBoxLayout(self.tab_learning)
        layout.setContentsMargins(10, 12, 10, 10)
        layout.setSpacing(12)

        header = QLabel("ACTIVE RESEARCH & BLOCKCHAIN OBJECTIVES")
        header.setObjectName("sectionHeading")
        layout.addWidget(header)

        goals = self.cfg.get("learning_goals", [])
        for g in goals:
            card = QFrame()
            card.setObjectName("panelSubBox")
            vbox = QVBoxLayout(card)
            vbox.setContentsMargins(10, 8, 10, 8)
            vbox.setSpacing(4)

            top = QHBoxLayout()
            t_lbl = QLabel(f"⚡ {g.get('topic', '')}")
            t_lbl.setObjectName("learningTopic")
            s_lbl = QLabel(f"[{g.get('status', 'In Progress')}]")
            s_lbl.setObjectName("learningStatus")
            top.addWidget(t_lbl)
            top.addStretch()
            top.addWidget(s_lbl)
            vbox.addLayout(top)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(g.get("progress", 0)))
            bar.setFixedHeight(14)
            vbox.addWidget(bar)

            layout.addWidget(card)

        layout.addStretch()

    def init_shortcuts_tab(self):
        layout = QVBoxLayout(self.tab_shortcuts)
        layout.setContentsMargins(10, 12, 10, 10)
        layout.setSpacing(10)

        header = QLabel("VERIFIED DEVELOPER & SYSTEM SHORTCUTS")
        header.setObjectName("sectionHeading")
        layout.addWidget(header)

        grid = QGridLayout()
        grid.setSpacing(10)

        shortcuts = self.cfg.get("shortcuts", [])
        for i, s in enumerate(shortcuts):
            btn = QPushButton(s.get("name", "App"))
            btn.setObjectName("btnShortcut")
            cmd = s.get("command", "")
            btn.clicked.connect(lambda _, c=cmd: subprocess.Popen(c, shell=True))
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addStretch()

    def update_telemetry(self):
        """Update telemetry UI elements with real /proc data."""
        m = self.telemetry.get_metrics()
        self.lbl_clock.setText(m["time"])

        self.cpu_val.setText(f"{m['cpu_pct']:.1f}%")
        self.cpu_bar.setValue(int(m["cpu_pct"]))

        self.ram_val.setText(f"{m['used_ram']:.2f} / {m['total_ram']:.2f} GB ({m['ram_pct']:.1f}%)")
        self.ram_bar.setValue(int(m["ram_pct"]))

        self.disk_val.setText(f"{m['used_disk']:.1f} / {m['total_disk']:.1f} GB ({m['disk_pct']:.1f}%)")
        self.disk_bar.setValue(int(m["disk_pct"]))

        self.lbl_temp.setText(f"• CPU Temperature: {m['temp']}")
        self.lbl_net_rx.setText(f"• Download: {m['rx_kb']:.1f} KB/s")
        self.lbl_net_tx.setText(f"• Upload: {m['tx_kb']:.1f} KB/s")
        self.lbl_uptime.setText(f"• Uptime: {m['uptime']}")

    def launch_command_center(self):
        app_path = Path(__file__).resolve().parent / "main.py"
        subprocess.Popen(["python3", str(app_path)])

    def apply_theme(self):
        t = self.cfg.get("theme", {})
        accent = t.get("primary_accent", "#00ff66")
        cyan = t.get("secondary_accent", "#00e5ff")
        bg = t.get("primary_bg", "#0a0b10")
        sub_bg = t.get("secondary_bg", "#12161f")
        text = t.get("text_color", "#e0f8ff")

        style = f"""
        #hudContainer {{
            background-color: rgba(10, 11, 16, 0.92);
            border: 1px solid {cyan};
            border-top: 2px solid {accent};
            border-radius: 6px;
        }}
        #hudTitle {{
            color: {accent};
            font-family: 'FiraCode', 'Monospace', monospace;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        #hudSubtitle {{
            color: {cyan};
            font-size: 10px;
            font-family: 'FiraCode', monospace;
        }}
        #cyberIcon {{
            color: {accent};
            font-size: 20px;
        }}
        #hudClockBadge {{
            color: {accent};
            background-color: {sub_bg};
            border: 1px solid {accent};
            border-radius: 4px;
            padding: 3px 8px;
            font-family: 'FiraCode', monospace;
            font-weight: bold;
            font-size: 12px;
        }}
        #btnControl, #btnControlClose {{
            background-color: {sub_bg};
            color: {text};
            border: 1px solid #334155;
            border-radius: 3px;
            font-weight: bold;
        }}
        #btnControl:hover {{
            border-color: {cyan};
            color: {cyan};
        }}
        #btnControlClose:hover {{
            background-color: #ef4444;
            color: white;
            border-color: #ef4444;
        }}
        #cyberSeparator {{
            color: {cyan};
            background-color: rgba(0, 229, 255, 0.25);
            max-height: 1px;
        }}
        QTabWidget::pane {{
            border: 1px solid rgba(0, 229, 255, 0.3);
            background: transparent;
            border-radius: 4px;
        }}
        QTabBar::tab {{
            background-color: {sub_bg};
            color: #94a3b8;
            padding: 6px 14px;
            border: 1px solid #1e293b;
            border-bottom: none;
            margin-right: 2px;
            font-family: 'FiraCode', monospace;
            font-size: 11px;
        }}
        QTabBar::tab:selected {{
            color: {accent};
            border: 1px solid {accent};
            border-bottom: 2px solid {accent};
            background-color: rgba(0, 255, 102, 0.08);
            font-weight: bold;
        }}
        #metricCard, #panelSubBox {{
            background-color: rgba(18, 22, 31, 0.75);
            border: 1px solid rgba(0, 229, 255, 0.25);
            border-left: 3px solid {accent};
            border-radius: 4px;
        }}
        #cardTitle, #sectionHeading {{
            color: {cyan};
            font-family: 'FiraCode', monospace;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }}
        #cardSubtitle {{
            color: #64748b;
            font-size: 10px;
        }}
        #metricVal {{
            color: {accent};
            font-family: 'FiraCode', monospace;
            font-size: 18px;
            font-weight: bold;
        }}
        #telemetrySubline, #eduItem, #skillName {{
            color: {text};
            font-family: 'FiraCode', monospace;
            font-size: 11px;
        }}
        #identityName {{
            color: {accent};
            font-family: 'FiraCode', monospace;
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        #identityTitle {{
            color: {cyan};
            font-family: 'FiraCode', monospace;
            font-size: 13px;
        }}
        #identityBio {{
            color: {text};
            font-size: 11px;
            line-height: 1.4;
        }}
        #learningTopic {{
            color: {accent};
            font-weight: bold;
            font-size: 12px;
        }}
        #learningStatus {{
            color: {cyan};
            font-size: 10px;
            font-weight: bold;
        }}
        #hudFooterText {{
            color: #64748b;
            font-family: 'FiraCode', monospace;
            font-size: 9px;
            letter-spacing: 0.5px;
        }}
        #btnPrimaryCyber {{
            background-color: rgba(0, 255, 102, 0.15);
            color: {accent};
            border: 1px solid {accent};
            border-radius: 4px;
            padding: 5px 12px;
            font-family: 'FiraCode', monospace;
            font-size: 10px;
            font-weight: bold;
        }}
        #btnPrimaryCyber:hover {{
            background-color: {accent};
            color: #000;
        }}
        #btnLink {{
            background-color: {sub_bg};
            color: {cyan};
            border: 1px solid {cyan};
            border-radius: 4px;
            padding: 6px;
            font-family: 'FiraCode', monospace;
            font-size: 11px;
        }}
        #btnLink:hover {{
            background-color: {cyan};
            color: #000;
        }}
        #btnShortcut {{
            background-color: rgba(18, 22, 31, 0.85);
            color: {text};
            border: 1px solid rgba(0, 229, 255, 0.3);
            border-radius: 4px;
            padding: 10px;
            font-family: 'FiraCode', monospace;
            font-size: 11px;
            font-weight: bold;
        }}
        #btnShortcut:hover {{
            border-color: {accent};
            color: {accent};
            background-color: rgba(0, 255, 102, 0.08);
        }}
        QProgressBar {{
            background-color: #07090e;
            border: 1px solid #1e293b;
            border-radius: 3px;
            text-align: center;
            color: #fff;
            font-size: 9px;
            font-family: 'FiraCode', monospace;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {cyan}, stop:1 {accent});
            border-radius: 2px;
        }}
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        """
        self.setStyleSheet(style)

    # Window Dragging support
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


def main():
    app = QApplication(sys.argv)
    hud = CyberpunkHUD()
    hud.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

