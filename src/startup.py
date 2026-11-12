#!/usr/bin/env python3
"""
Victor Command Center - Animated Cyberpunk Startup Experience
Futuristic, lightweight post-login welcome screen with real hardware status,
cyberpunk terminal typing effect, progress bar, and instant Esc skip.
"""

import argparse
import os
import sys
import time
from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QKeyEvent, QPainter
from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QTextEdit, QVBoxLayout, QWidget
)

# Ensure local config can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import load_config


class StartupAnimationWindow(QWidget):
    """Futuristic Cyberpunk Startup Screen."""

    def __init__(self, preview_mode: bool = False):
        super().__init__()
        self.preview_mode = preview_mode
        self.cfg = load_config()
        self.startup_cfg = self.cfg.get("startup", {})
        self.prof_cfg = self.cfg.get("profile", {})
        self.theme_cfg = self.cfg.get("theme", {})

        # Animation states
        self.current_msg_idx = 0
        self.current_char_idx = 0
        self.messages = []
        self.total_duration_ms = int(self.startup_cfg.get("duration_ms", 3800))
        self.speed = float(self.startup_cfg.get("animation_speed", 1.0))
        self.typing_enabled = bool(self.startup_cfg.get("typing_effect", True))
        self.show_sys_info = bool(self.startup_cfg.get("show_system_info", True))

        self.prepare_messages()
        self.init_ui()

        # Step timers
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.type_next_char)

        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)

        # Safety watchdog: guarantee window closes even if timers fail
        self.watchdog_timer = QTimer(self)
        self.watchdog_timer.setSingleShot(True)
        max_safety_ms = max(5000, int(self.total_duration_ms * 1.5))
        self.watchdog_timer.timeout.connect(self.finish_and_exit)
        self.watchdog_timer.start(max_safety_ms)

        # Start animation
        self.start_time = time.time()
        self.progress_val = 0.0
        self.progress_timer.start(30)
        self.typing_timer.start(int(max(10, 22 / self.speed)))

    def prepare_messages(self):
        """Build initialization messages with real system metrics."""
        raw_msgs = self.startup_cfg.get("messages", [])

        # Gather real system facts
        cpu_name = "Intel Processor"
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        cpu_name = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass

        ram_gb = "8.0 GB"
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        ram_gb = f"{int(line.split()[1]) / 1024 / 1024:.1f} GB"
                        break
        except Exception:
            pass

        kernel = os.uname().release
        hostname = os.uname().nodename

        self.messages = []
        for m in raw_msgs:
            formatted = m.replace("{CPU}", cpu_name).replace("{RAM}", ram_gb).replace("{KERNEL}", kernel).replace("{HOST}", hostname)
            self.messages.append(formatted)

        if self.show_sys_info:
            self.messages.insert(1, f"[HARDWARE] {cpu_name} | {ram_gb} RAM Active")
            self.messages.insert(2, f"[KERNEL] Linux {kernel} on {hostname}")

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        if self.preview_mode:
            self.resize(780, 520)
            # Center on screen
            screen = QApplication.primaryScreen().geometry()
            self.move((screen.width() - 780) // 2, (screen.height() - 520) // 2)
        else:
            screen = QApplication.primaryScreen().geometry()
            self.setGeometry(screen)

        accent = self.theme_cfg.get("primary_accent", "#00ff66")
        cyan = self.theme_cfg.get("secondary_accent", "#00e5ff")
        bg = "#07080b"

        self.setStyleSheet(f"""
        QWidget {{
            background-color: {bg};
            color: #e0f8ff;
            font-family: 'FiraCode', 'Monospace', monospace;
        }}
        #topBar {{
            border-bottom: 1px solid rgba(0, 229, 255, 0.3);
            padding: 8px 16px;
        }}
        #lblSystemTitle {{
            color: {cyan};
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        #btnSkip {{
            background-color: rgba(0, 229, 255, 0.1);
            color: {cyan};
            border: 1px solid {cyan};
            border-radius: 3px;
            padding: 4px 10px;
            font-size: 10px;
            font-weight: bold;
        }}
        #btnSkip:hover {{
            background-color: {cyan};
            color: #000;
        }}
        #heroName {{
            color: {accent};
            font-size: 26px;
            font-weight: bold;
            letter-spacing: 2px;
        }}
        #heroTitle {{
            color: {cyan};
            font-size: 13px;
            letter-spacing: 1px;
        }}
        #terminalBox {{
            background-color: #0c0e14;
            border: 1px solid rgba(0, 255, 102, 0.3);
            border-left: 3px solid {accent};
            border-radius: 4px;
            padding: 12px;
            font-size: 11px;
            color: #d1fae5;
        }}
        QProgressBar {{
            background-color: #0c0e14;
            border: 1px solid #1e293b;
            border-radius: 4px;
            height: 18px;
            text-align: center;
            color: #ffffff;
            font-size: 10px;
            font-weight: bold;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {cyan}, stop:1 {accent});
            border-radius: 3px;
        }}
        #statusNote {{
            color: #64748b;
            font-size: 10px;
        }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 20)
        main_layout.setSpacing(14)

        # 1. Top Header Bar
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)

        lbl_top = QLabel("⚡ VICTOR COMMAND CENTER // INITIALIZATION PROTOCOL")
        lbl_top.setObjectName("lblSystemTitle")
        top_layout.addWidget(lbl_top)
        top_layout.addStretch()

        btn_skip = QPushButton("ESC TO SKIP ❯")
        btn_skip.setObjectName("btnSkip")
        btn_skip.clicked.connect(self.finish_and_exit)
        top_layout.addWidget(btn_skip)
        main_layout.addWidget(top_bar)

        # 2. Identity Hero Header
        hero_box = QVBoxLayout()
        hero_box.setSpacing(2)
        name_str = self.prof_cfg.get("name", "VICTOR ODUOR").upper()
        self.lbl_name = QLabel(f"// {name_str}")
        self.lbl_name.setObjectName("heroName")
        hero_box.addWidget(self.lbl_name)

        title_str = self.prof_cfg.get("title", "Software Developer & ICT Professional")
        self.lbl_title = QLabel(f">> {title_str} // Technical University of Mombasa")
        self.lbl_title.setObjectName("heroTitle")
        hero_box.addWidget(self.lbl_title)
        main_layout.addLayout(hero_box)

        # 3. Terminal Log Output Box
        self.term_output = QTextEdit()
        self.term_output.setObjectName("terminalBox")
        self.term_output.setReadOnly(True)
        main_layout.addWidget(self.term_output, stretch=1)

        # 4. Animated Cyberpunk Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # 5. Bottom Status Note
        footer_box = QHBoxLayout()
        self.lbl_footer = QLabel("[SYS_STATUS] Initializing user environment... Click anywhere or press ESC to bypass.")
        self.lbl_footer.setObjectName("statusNote")
        footer_box.addWidget(self.lbl_footer)
        footer_box.addStretch()
        lbl_mode = QLabel("MODE: POST-LOGIN WORKSTATION" if not self.preview_mode else "MODE: LIVE PREVIEW")
        lbl_mode.setObjectName("statusNote")
        footer_box.addWidget(lbl_mode)
        main_layout.addLayout(footer_box)

    def type_next_char(self):
        """Simulate terminal typing effect for messages."""
        if self.current_msg_idx >= len(self.messages):
            self.typing_timer.stop()
            return

        target_msg = self.messages[self.current_msg_idx]

        if not self.typing_enabled:
            # If typing effect disabled, output entire line immediately
            self.term_output.append(f"> {target_msg}")
            self.current_msg_idx += 1
            return

        if self.current_char_idx == 0:
            self.term_output.append("> ")

        if self.current_char_idx < len(target_msg):
            # Append next character
            cursor = self.term_output.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(target_msg[self.current_char_idx])
            self.term_output.setTextCursor(cursor)
            self.current_char_idx += 1
        else:
            # Move to next line
            self.current_msg_idx += 1
            self.current_char_idx = 0

    def update_progress(self):
        """Update progress bar smoothly based on elapsed duration."""
        elapsed = (time.time() - self.start_time) * 1000.0
        progress = min(100.0, (elapsed / self.total_duration_ms) * 100.0)
        self.progress_bar.setValue(int(progress))
        self.progress_bar.setFormat(f"INITIALIZING WORKSTATION... {int(progress)}%")

        if progress >= 100.0:
            self.progress_timer.stop()
            self.lbl_footer.setText("[SYS_STATUS] Initialization complete. Loading desktop session...")
            QTimer.singleShot(400, self.finish_and_exit)

    def keyPressEvent(self, event: QKeyEvent):
        """Allow manual skip via Esc, Enter, Space, or Q."""
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Space, Qt.Key.Key_Q):
            self.finish_and_exit()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Allow clicking anywhere to immediately skip."""
        self.finish_and_exit()

    def finish_and_exit(self):
        """Cleanly terminate animation and transition to desktop."""
        self.typing_timer.stop()
        self.progress_timer.stop()
        self.watchdog_timer.stop()
        self.close()
        QApplication.quit()


def main():
    parser = argparse.ArgumentParser(description="Victor Command Center - Animated Startup")
    parser.add_argument("--preview", action="store_true", help="Launch in preview window mode")
    parser.add_argument("--force", action="store_true", help="Launch even if disabled in config")
    args = parser.parse_args()

    cfg = load_config()
    startup_cfg = cfg.get("startup", {})

    # Check if enabled
    if not args.preview and not args.force:
        if not startup_cfg.get("enabled", True):
            print("[INFO] Startup animation disabled in configuration. Exiting immediately.")
            return

    app = QApplication(sys.argv)
    window = StartupAnimationWindow(preview_mode=args.preview)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

