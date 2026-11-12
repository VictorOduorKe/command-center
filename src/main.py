#!/usr/bin/env python3
"""
Victor Command Center - Desktop Management Application
Unified control center for personal profile, skills, projects, learning tracks,
startup animation, theme customization, and automated desktop backups/restores.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QColorDialog, QComboBox, QDialog, QFileDialog,
    QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QProgressBar, QPushButton, QScrollArea, QSlider,
    QSpinBox, QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget
)

# Import local engines
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    DEFAULT_CONFIG, THEME_PRESETS, create_backup, list_backups,
    load_config, restore_backup, save_config
)
from restore import restore_factory_desktop, uninstall_command_center
from desktop_integrator import apply_full_desktop_theme, PRESET_PROFILES


class VictorCommandCenter(QWidget):
    """Main Management Application Window."""

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle("Victor Command Center // Workstation Manager")
        self.resize(1020, 720)
        self.setMinimumSize(850, 600)

        # Set Window Icon if present
        icon_path = Path("/home/alpha/victor-command-center/assets/victor-command-center.svg")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # 1. Header Banner
        header = QFrame()
        header.setObjectName("appHeader")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(14, 10, 14, 10)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        lbl_h1 = QLabel("VICTOR COMMAND CENTER")
        lbl_h1.setObjectName("appHeaderTitle")
        lbl_h2 = QLabel("PERSONAL WORKSTATION MANAGEMENT & CYBERPUNK CONTROL SUITE")
        lbl_h2.setObjectName("appHeaderSubtitle")
        title_vbox.addWidget(lbl_h1)
        title_vbox.addWidget(lbl_h2)
        h_layout.addLayout(title_vbox)

        h_layout.addStretch()

        btn_hud = QPushButton("OPEN DESKTOP HUD")
        btn_hud.setObjectName("btnCyberHeader")
        btn_hud.clicked.connect(self.launch_hud)
        h_layout.addWidget(btn_hud)

        btn_term = QPushButton("OPEN TERMINAL")
        btn_term.setObjectName("btnCyberHeader")
        btn_term.clicked.connect(lambda: subprocess.Popen(["qterminal"]))
        h_layout.addWidget(btn_term)

        main_layout.addWidget(header)

        # 2. Main Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")

        # Tab 1: Profile & Identity
        self.tab_profile = QWidget()
        self.init_profile_tab()
        self.tabs.addTab(self.tab_profile, "PROFILE & IDENTITY")

        # Tab 2: Skills Matrix
        self.tab_skills = QWidget()
        self.init_skills_tab()
        self.tabs.addTab(self.tab_skills, "SKILLS MATRIX")

        # Tab 3: Projects Portfolio
        self.tab_projects = QWidget()
        self.init_projects_tab()
        self.tabs.addTab(self.tab_projects, "PROJECTS")

        # Tab 4: Learning Tracker
        self.tab_learning = QWidget()
        self.init_learning_tab()
        self.tabs.addTab(self.tab_learning, "LEARNING TRACKS")

        # Tab 5: Startup Animation Editor
        self.tab_startup = QWidget()
        self.init_startup_tab()
        self.tabs.addTab(self.tab_startup, "STARTUP EDITOR")

        # Tab 6: Theme Customizer
        self.tab_theme = QWidget()
        self.init_theme_tab()
        self.tabs.addTab(self.tab_theme, "THEME & VISUALS")

        # Tab 7: Backup & Desktop Restore
        self.tab_restore = QWidget()
        self.init_restore_tab()
        self.tabs.addTab(self.tab_restore, "BACKUPS & RESTORE")

        main_layout.addWidget(self.tabs, stretch=1)

        # 3. Footer Bar
        footer = QHBoxLayout()
        self.lbl_status = QLabel("Ready. Configurations validated and loaded from ~/.config/victor-command-center/config.json")
        self.lbl_status.setObjectName("footerStatus")
        footer.addWidget(self.lbl_status)
        footer.addStretch()

        btn_save_all = QPushButton("SAVE ALL CHANGES")
        btn_save_all.setObjectName("btnSavePrimary")
        btn_save_all.clicked.connect(self.save_all_settings)
        footer.addWidget(btn_save_all)

        main_layout.addLayout(footer)

    # -------------------------------------------------------------
    # TAB 1: PROFILE MANAGEMENT
    # -------------------------------------------------------------
    def init_profile_tab(self):
        layout = QVBoxLayout(self.tab_profile)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("contentScroll")
        form_w = QWidget()
        form_layout = QFormLayout(form_w)
        form_layout.setSpacing(10)

        p = self.cfg.get("profile", {})
        self.txt_name = QLineEdit(p.get("name", "Victor Oduor"))
        self.txt_title = QLineEdit(p.get("title", "Software Developer & ICT Professional"))
        self.txt_inst = QLineEdit(p.get("institution", "Technical University of Mombasa"))
        self.txt_deg = QLineEdit(p.get("degree", "Bachelor of Information and Communication Technology"))
        self.txt_github = QLineEdit(p.get("github", "https://github.com/VictorOduorKe"))
        self.txt_linkedin = QLineEdit(p.get("linkedin", "https://www.linkedin.com/in/Victor-Oduor-ke/"))
        self.txt_motto = QLineEdit(p.get("motto", ""))
        self.txt_bio = QTextEdit(p.get("bio", ""))
        self.txt_bio.setMaximumHeight(90)

        form_layout.addRow("Full Name:", self.txt_name)
        form_layout.addRow("Professional Title:", self.txt_title)
        form_layout.addRow("Degree Program:", self.txt_deg)
        form_layout.addRow("Institution:", self.txt_inst)
        form_layout.addRow("Personal Motto:", self.txt_motto)
        form_layout.addRow("GitHub Profile URL:", self.txt_github)
        form_layout.addRow("LinkedIn Profile URL:", self.txt_linkedin)
        form_layout.addRow("Personal Bio / Intro:", self.txt_bio)

        scroll.setWidget(form_w)
        layout.addWidget(scroll)

        btn_save_profile = QPushButton("Apply Profile Updates")
        btn_save_profile.setObjectName("btnTabAction")
        btn_save_profile.clicked.connect(self.save_profile_data)
        layout.addWidget(btn_save_profile, alignment=Qt.AlignmentFlag.AlignRight)

    def save_profile_data(self, notify: bool = True):
        p = self.cfg.setdefault("profile", {})
        p["name"] = self.txt_name.text().strip()
        p["title"] = self.txt_title.text().strip()
        p["degree"] = self.txt_deg.text().strip()
        p["institution"] = self.txt_inst.text().strip()
        p["motto"] = self.txt_motto.text().strip()
        p["github"] = self.txt_github.text().strip()
        p["linkedin"] = self.txt_linkedin.text().strip()
        p["bio"] = self.txt_bio.toPlainText().strip()

        save_config(self.cfg, backup=True, label="profile_edit")
        self.lbl_status.setText(f"Profile updated successfully for {p['name']}.")
        if notify:
            QMessageBox.information(self, "Profile Saved", "Personal profile updated. Desktop HUD will reflect changes.")

    # -------------------------------------------------------------
    # TAB 2: TECHNICAL SKILLS MATRIX
    # -------------------------------------------------------------
    def init_skills_tab(self):
        layout = QVBoxLayout(self.tab_skills)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Table
        self.tbl_skills = QTableWidget()
        self.tbl_skills.setColumnCount(4)
        self.tbl_skills.setHorizontalHeaderLabels(["Skill Name", "Category", "Proficiency Level", "Rating (%)"])
        self.tbl_skills.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_skills.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_skills.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_skills.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_skills.setObjectName("cyberTable")

        self.populate_skills_table()
        layout.addWidget(self.tbl_skills)

        # Action Buttons
        btn_bar = QHBoxLayout()
        btn_add = QPushButton("+ Add New Skill")
        btn_add.setObjectName("btnTabAction")
        btn_add.clicked.connect(self.add_skill_dialog)

        btn_del = QPushButton("− Remove Selected")
        btn_del.setObjectName("btnDangerAction")
        btn_del.clicked.connect(self.remove_selected_skill)

        btn_save_skills = QPushButton("Save Skills Matrix")
        btn_save_skills.setObjectName("btnTabAction")
        btn_save_skills.clicked.connect(self.save_skills_data)

        btn_bar.addWidget(btn_add)
        btn_bar.addWidget(btn_del)
        btn_bar.addStretch()
        btn_bar.addWidget(btn_save_skills)
        layout.addLayout(btn_bar)

    def populate_skills_table(self):
        skills = self.cfg.get("skills", [])
        self.tbl_skills.setRowCount(len(skills))
        for row, s in enumerate(skills):
            self.tbl_skills.setItem(row, 0, QTableWidgetItem(s.get("name", "")))
            self.tbl_skills.setItem(row, 1, QTableWidgetItem(s.get("category", "")))
            self.tbl_skills.setItem(row, 2, QTableWidgetItem(s.get("level", "")))
            self.tbl_skills.setItem(row, 3, QTableWidgetItem(str(s.get("proficiency", 50))))

    def add_skill_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Technical Skill")
        d_layout = QFormLayout(dlg)

        inp_name = QLineEdit()
        cb_cat = QComboBox()
        cb_cat.addItems(["Frontend", "Backend", "Databases", "Networking", "Cybersecurity", "Cloud", "Blockchain"])
        cb_lvl = QComboBox()
        cb_lvl.addItems(["established", "learning", "future_goal"])
        sp_prof = QSpinBox()
        sp_prof.setRange(1, 100)
        sp_prof.setValue(75)

        d_layout.addRow("Skill Name:", inp_name)
        d_layout.addRow("Category:", cb_cat)
        d_layout.addRow("Proficiency Tier:", cb_lvl)
        d_layout.addRow("Proficiency %:", sp_prof)

        btn_box = QHBoxLayout()
        b_ok = QPushButton("Add")
        b_ok.clicked.connect(dlg.accept)
        b_cancel = QPushButton("Cancel")
        b_cancel.clicked.connect(dlg.reject)
        btn_box.addWidget(b_ok)
        btn_box.addWidget(b_cancel)
        d_layout.addRow(btn_box)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = inp_name.text().strip()
            if name:
                self.cfg.setdefault("skills", []).append({
                    "name": name,
                    "category": cb_cat.currentText(),
                    "level": cb_lvl.currentText(),
                    "proficiency": sp_prof.value()
                })
                self.populate_skills_table()

    def remove_selected_skill(self):
        row = self.tbl_skills.currentRow()
        if row >= 0:
            skills = self.cfg.get("skills", [])
            if row < len(skills):
                del skills[row]
                self.populate_skills_table()

    def save_skills_data(self, notify: bool = True):
        # Read table back into config
        new_skills = []
        for row in range(self.tbl_skills.rowCount()):
            name = self.tbl_skills.item(row, 0).text().strip()
            cat = self.tbl_skills.item(row, 1).text().strip()
            lvl = self.tbl_skills.item(row, 2).text().strip()
            try:
                prof = int(self.tbl_skills.item(row, 3).text().strip())
            except ValueError:
                prof = 50
            if name:
                new_skills.append({"name": name, "category": cat, "level": lvl, "proficiency": prof})

        self.cfg["skills"] = new_skills
        save_config(self.cfg, backup=True, label="skills_edit")
        self.lbl_status.setText(f"Skills matrix saved ({len(new_skills)} skills).")
        if notify:
            QMessageBox.information(self, "Skills Saved", "Technical skills matrix saved successfully.")

    # -------------------------------------------------------------
    # TAB 3: PROJECTS PORTFOLIO
    # -------------------------------------------------------------
    def init_projects_tab(self):
        layout = QVBoxLayout(self.tab_projects)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.tbl_projects = QTableWidget()
        self.tbl_projects.setColumnCount(4)
        self.tbl_projects.setHorizontalHeaderLabels(["Project Name", "Description", "Tech Stack", "Repository URL"])
        self.tbl_projects.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_projects.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl_projects.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_projects.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_projects.setObjectName("cyberTable")

        self.populate_projects_table()
        layout.addWidget(self.tbl_projects)

        btn_bar = QHBoxLayout()
        btn_add = QPushButton("+ Add Project")
        btn_add.setObjectName("btnTabAction")
        btn_add.clicked.connect(self.add_project_dialog)

        btn_del = QPushButton("− Remove Selected")
        btn_del.setObjectName("btnDangerAction")
        btn_del.clicked.connect(self.remove_selected_project)

        btn_save = QPushButton("Save Projects")
        btn_save.setObjectName("btnTabAction")
        btn_save.clicked.connect(self.save_projects_data)

        btn_bar.addWidget(btn_add)
        btn_bar.addWidget(btn_del)
        btn_bar.addStretch()
        btn_bar.addWidget(btn_save)
        layout.addLayout(btn_bar)

    def populate_projects_table(self):
        projects = self.cfg.get("projects", [])
        self.tbl_projects.setRowCount(len(projects))
        for row, p in enumerate(projects):
            self.tbl_projects.setItem(row, 0, QTableWidgetItem(p.get("name", "")))
            self.tbl_projects.setItem(row, 1, QTableWidgetItem(p.get("description", "")))
            self.tbl_projects.setItem(row, 2, QTableWidgetItem(p.get("tech", "")))
            self.tbl_projects.setItem(row, 3, QTableWidgetItem(p.get("url", "")))

    def add_project_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Project")
        d_layout = QFormLayout(dlg)

        inp_name = QLineEdit()
        inp_desc = QLineEdit()
        inp_tech = QLineEdit()
        inp_url = QLineEdit("https://github.com/VictorOduorKe")

        d_layout.addRow("Project Name:", inp_name)
        d_layout.addRow("Description:", inp_desc)
        d_layout.addRow("Tech Stack:", inp_tech)
        d_layout.addRow("URL:", inp_url)

        btn_box = QHBoxLayout()
        b_ok = QPushButton("Add")
        b_ok.clicked.connect(dlg.accept)
        b_cancel = QPushButton("Cancel")
        b_cancel.clicked.connect(dlg.reject)
        btn_box.addWidget(b_ok)
        btn_box.addWidget(b_cancel)
        d_layout.addRow(btn_box)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            if inp_name.text().strip():
                self.cfg.setdefault("projects", []).append({
                    "name": inp_name.text().strip(),
                    "description": inp_desc.text().strip(),
                    "tech": inp_tech.text().strip(),
                    "url": inp_url.text().strip()
                })
                self.populate_projects_table()

    def remove_selected_project(self):
        row = self.tbl_projects.currentRow()
        if row >= 0:
            projects = self.cfg.get("projects", [])
            if row < len(projects):
                del projects[row]
                self.populate_projects_table()

    def save_projects_data(self, notify: bool = True):
        new_projects = []
        for r in range(self.tbl_projects.rowCount()):
            name = self.tbl_projects.item(r, 0).text().strip()
            desc = self.tbl_projects.item(r, 1).text().strip()
            tech = self.tbl_projects.item(r, 2).text().strip()
            url = self.tbl_projects.item(r, 3).text().strip()
            if name:
                new_projects.append({"name": name, "description": desc, "tech": tech, "url": url})
        self.cfg["projects"] = new_projects
        save_config(self.cfg, backup=True, label="projects_edit")
        self.lbl_status.setText(f"Projects portfolio saved ({len(new_projects)} projects).")
        if notify:
            QMessageBox.information(self, "Projects Saved", "Projects portfolio updated.")

    # -------------------------------------------------------------
    # TAB 4: LEARNING GOALS
    # -------------------------------------------------------------
    def init_learning_tab(self):
        layout = QVBoxLayout(self.tab_learning)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.tbl_learning = QTableWidget()
        self.tbl_learning.setColumnCount(3)
        self.tbl_learning.setHorizontalHeaderLabels(["Research Topic / Objective", "Status", "Progress (%)"])
        self.tbl_learning.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_learning.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_learning.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_learning.setObjectName("cyberTable")

        self.populate_learning_table()
        layout.addWidget(self.tbl_learning)

        btn_bar = QHBoxLayout()
        btn_add = QPushButton("+ Add Learning Goal")
        btn_add.setObjectName("btnTabAction")
        btn_add.clicked.connect(self.add_learning_dialog)

        btn_del = QPushButton("− Remove Selected")
        btn_del.setObjectName("btnDangerAction")
        btn_del.clicked.connect(self.remove_selected_goal)

        btn_save = QPushButton("Save Learning Goals")
        btn_save.setObjectName("btnTabAction")
        btn_save.clicked.connect(self.save_learning_data)

        btn_bar.addWidget(btn_add)
        btn_bar.addWidget(btn_del)
        btn_bar.addStretch()
        btn_bar.addWidget(btn_save)
        layout.addLayout(btn_bar)

    def populate_learning_table(self):
        goals = self.cfg.get("learning_goals", [])
        self.tbl_learning.setRowCount(len(goals))
        for r, g in enumerate(goals):
            self.tbl_learning.setItem(r, 0, QTableWidgetItem(g.get("topic", "")))
            self.tbl_learning.setItem(r, 1, QTableWidgetItem(g.get("status", "In Progress")))
            self.tbl_learning.setItem(r, 2, QTableWidgetItem(str(g.get("progress", 50))))

    def add_learning_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Learning Goal")
        d_layout = QFormLayout(dlg)

        inp_top = QLineEdit()
        cb_stat = QComboBox()
        cb_stat.addItems(["In Progress", "Planned", "Completed"])
        sp_prog = QSpinBox()
        sp_prog.setRange(0, 100)
        sp_prog.setValue(50)

        d_layout.addRow("Topic / Milestone:", inp_top)
        d_layout.addRow("Status:", cb_stat)
        d_layout.addRow("Progress %:", sp_prog)

        btn_box = QHBoxLayout()
        b_ok = QPushButton("Add")
        b_ok.clicked.connect(dlg.accept)
        b_cancel = QPushButton("Cancel")
        b_cancel.clicked.connect(dlg.reject)
        btn_box.addWidget(b_ok)
        btn_box.addWidget(b_cancel)
        d_layout.addRow(btn_box)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            if inp_top.text().strip():
                self.cfg.setdefault("learning_goals", []).append({
                    "topic": inp_top.text().strip(),
                    "status": cb_stat.currentText(),
                    "progress": sp_prog.value()
                })
                self.populate_learning_table()

    def remove_selected_goal(self):
        row = self.tbl_learning.currentRow()
        if row >= 0:
            goals = self.cfg.get("learning_goals", [])
            if row < len(goals):
                del goals[row]
                self.populate_learning_table()

    def save_learning_data(self, notify: bool = True):
        new_goals = []
        for r in range(self.tbl_learning.rowCount()):
            top = self.tbl_learning.item(r, 0).text().strip()
            stat = self.tbl_learning.item(r, 1).text().strip()
            try:
                prog = int(self.tbl_learning.item(r, 2).text().strip())
            except ValueError:
                prog = 0
            if top:
                new_goals.append({"topic": top, "status": stat, "progress": prog})
        self.cfg["learning_goals"] = new_goals
        save_config(self.cfg, backup=True, label="learning_edit")
        self.lbl_status.setText("Learning tracks updated.")
        if notify:
            QMessageBox.information(self, "Learning Saved", "Learning goals and blockchain tracks updated.")

    # -------------------------------------------------------------
    # TAB 5: STARTUP ANIMATION EDITOR
    # -------------------------------------------------------------
    def init_startup_tab(self):
        layout = QVBoxLayout(self.tab_startup)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        st = self.cfg.get("startup", {})

        top_controls = QHBoxLayout()
        self.cb_startup_enabled = QComboBox()
        self.cb_startup_enabled.addItems(["Enabled", "Disabled"])
        self.cb_startup_enabled.setCurrentIndex(0 if st.get("enabled", True) else 1)
        top_controls.addWidget(QLabel("Startup Animation:"))
        top_controls.addWidget(self.cb_startup_enabled)

        top_controls.addSpacing(20)

        self.cb_typing = QComboBox()
        self.cb_typing.addItems(["Typing Animation Enabled", "Instant Display"])
        self.cb_typing.setCurrentIndex(0 if st.get("typing_effect", True) else 1)
        top_controls.addWidget(self.cb_typing)

        top_controls.addSpacing(20)

        self.cb_sysinfo_startup = QComboBox()
        self.cb_sysinfo_startup.addItems(["Show Real System Status", "Hide System Status"])
        self.cb_sysinfo_startup.setCurrentIndex(0 if st.get("show_system_info", True) else 1)
        top_controls.addWidget(self.cb_sysinfo_startup)

        top_controls.addStretch()
        layout.addLayout(top_controls)

        # Duration & Speed Sliders
        sliders_box = QGridLayout()
        sliders_box.addWidget(QLabel("Duration:"), 0, 0)
        self.slider_duration = QSlider(Qt.Orientation.Horizontal)
        self.slider_duration.setRange(2000, 8000)
        self.slider_duration.setValue(int(st.get("duration_ms", 3800)))
        self.lbl_dur_val = QLabel(f"{st.get('duration_ms', 3800)} ms")
        self.slider_duration.valueChanged.connect(lambda v: self.lbl_dur_val.setText(f"{v} ms"))
        sliders_box.addWidget(self.slider_duration, 0, 1)
        sliders_box.addWidget(self.lbl_dur_val, 0, 2)

        sliders_box.addWidget(QLabel("Animation Speed:"), 1, 0)
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(5, 25)
        self.slider_speed.setValue(int(st.get("animation_speed", 1.0) * 10))
        self.lbl_speed_val = QLabel(f"{st.get('animation_speed', 1.0):.1f}x")
        self.slider_speed.valueChanged.connect(lambda v: self.lbl_speed_val.setText(f"{v/10:.1f}x"))
        sliders_box.addWidget(self.slider_speed, 1, 1)
        sliders_box.addWidget(self.lbl_speed_val, 1, 2)

        layout.addLayout(sliders_box)

        # Message List Editor
        layout.addWidget(QLabel("Startup Initialization Messages Sequence:"))
        self.list_msgs = QListWidget()
        self.list_msgs.setObjectName("cyberList")
        for m in st.get("messages", []):
            self.list_msgs.addItem(m)
        layout.addWidget(self.list_msgs)

        msg_btn_bar = QHBoxLayout()
        btn_add_msg = QPushButton("+ Add Message")
        btn_add_msg.clicked.connect(self.add_startup_msg)
        btn_del_msg = QPushButton("− Remove Selected")
        btn_del_msg.clicked.connect(self.del_startup_msg)
        btn_up = QPushButton("▲ Move Up")
        btn_up.clicked.connect(self.move_msg_up)
        btn_down = QPushButton("▼ Move Down")
        btn_down.clicked.connect(self.move_msg_down)

        msg_btn_bar.addWidget(btn_add_msg)
        msg_btn_bar.addWidget(btn_del_msg)
        msg_btn_bar.addWidget(btn_up)
        msg_btn_bar.addWidget(btn_down)
        msg_btn_bar.addStretch()

        # PREVIEW BUTTON
        btn_preview = QPushButton("⚡ PREVIEW STARTUP ANIMATION")
        btn_preview.setObjectName("btnPreviewCyber")
        btn_preview.clicked.connect(self.preview_startup_animation)
        msg_btn_bar.addWidget(btn_preview)

        btn_save_startup = QPushButton("Save Startup Settings")
        btn_save_startup.setObjectName("btnTabAction")
        btn_save_startup.clicked.connect(self.save_startup_settings)
        msg_btn_bar.addWidget(btn_save_startup)

        layout.addLayout(msg_btn_bar)

    def add_startup_msg(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Startup Message")
        l = QVBoxLayout(dlg)
        txt = QLineEdit("[CUSTOM] System check complete...")
        l.addWidget(QLabel("Message text:"))
        l.addWidget(txt)
        btn = QPushButton("Add")
        btn.clicked.connect(dlg.accept)
        l.addWidget(btn)
        if dlg.exec() == QDialog.DialogCode.Accepted and txt.text().strip():
            self.list_msgs.addItem(txt.text().strip())

    def del_startup_msg(self):
        row = self.list_msgs.currentRow()
        if row >= 0:
            self.list_msgs.takeItem(row)

    def move_msg_up(self):
        row = self.list_msgs.currentRow()
        if row > 0:
            item = self.list_msgs.takeItem(row)
            self.list_msgs.insertItem(row - 1, item)
            self.list_msgs.setCurrentRow(row - 1)

    def move_msg_down(self):
        row = self.list_msgs.currentRow()
        if row < self.list_msgs.count() - 1:
            item = self.list_msgs.takeItem(row)
            self.list_msgs.insertItem(row + 1, item)
            self.list_msgs.setCurrentRow(row + 1)

    def preview_startup_animation(self):
        # Save temporary settings and spawn startup script with --preview
        self.save_startup_settings(notify=False)
        startup_script = Path(__file__).resolve().parent / "startup.py"
        subprocess.Popen(["python3", str(startup_script), "--preview"])

    def save_startup_settings(self, notify: bool = True):
        st = self.cfg.setdefault("startup", {})
        st["enabled"] = (self.cb_startup_enabled.currentIndex() == 0)
        st["typing_effect"] = (self.cb_typing.currentIndex() == 0)
        st["show_system_info"] = (self.cb_sysinfo_startup.currentIndex() == 0)
        st["duration_ms"] = self.slider_duration.value()
        st["animation_speed"] = self.slider_speed.value() / 10.0

        msgs = []
        for i in range(self.list_msgs.count()):
            msgs.append(self.list_msgs.item(i).text())
        st["messages"] = msgs

        save_config(self.cfg, backup=True, label="startup_edit")
        self.lbl_status.setText("Startup animation settings saved.")
        if notify:
            QMessageBox.information(self, "Startup Saved", "Startup settings and initialization sequence updated.")

    # -------------------------------------------------------------
    # TAB 6: THEME EDITOR
    # -------------------------------------------------------------
    def init_theme_tab(self):
        layout = QVBoxLayout(self.tab_theme)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        t = self.cfg.get("theme", {})

        # Presets selector
        top_box = QHBoxLayout()
        top_box.addWidget(QLabel("Theme Preset:"))
        self.cb_preset = QComboBox()
        self.cb_preset.addItems(list(PRESET_PROFILES.keys()))
        current_preset = t.get("preset", "Cyberpunk Green")
        idx = self.cb_preset.findText(current_preset)
        if idx >= 0:
            self.cb_preset.setCurrentIndex(idx)
        self.cb_preset.currentTextChanged.connect(self.on_preset_changed)
        top_box.addWidget(self.cb_preset)
        top_box.addStretch()
        layout.addLayout(top_box)

        # XFCE Component Controls Group
        comp_group = QGroupBox("Actual XFCE Desktop Component Controls")
        comp_group.setObjectName("restoreGroup")
        cg_layout = QGridLayout(comp_group)
        cg_layout.setSpacing(8)

        # Window Manager
        cg_layout.addWidget(QLabel("Window Manager Theme:"), 0, 0)
        self.cb_xfwm = QComboBox()
        self.cb_xfwm.addItems(["Victor-Cyberpunk", "Kali-Dark", "Kali-Teal-Dark"])
        cg_layout.addWidget(self.cb_xfwm, 0, 1)

        # Icons
        cg_layout.addWidget(QLabel("Icon Theme:"), 0, 2)
        self.cb_icons = QComboBox()
        self.cb_icons.addItems(["Flat-Remix-Green-Dark", "Flat-Remix-Blue-Dark", "Flat-Remix-Teal-Dark"])
        cg_layout.addWidget(self.cb_icons, 0, 3)

        # Top Panel
        cg_layout.addWidget(QLabel("Top Panel Mode:"), 1, 0)
        self.cb_top_panel = QComboBox()
        self.cb_top_panel.addItems(["Cyberpunk Navigation (Whiskermenu + Monitor)", "Standard"])
        cg_layout.addWidget(self.cb_top_panel, 1, 1)

        # Bottom Dock
        cg_layout.addWidget(QLabel("Bottom Dock Mode:"), 1, 2)
        self.cb_bottom_dock = QComboBox()
        self.cb_bottom_dock.addItems(["Centered Application Dock", "Standard Taskbar"])
        cg_layout.addWidget(self.cb_bottom_dock, 1, 3)

        # Desktop Widget (Conky)
        cg_layout.addWidget(QLabel("Desktop Conky HUD:"), 2, 0)
        self.cb_conky = QComboBox()
        self.cb_conky.addItems(["Embedded Desktop Conky Widget (Enabled)", "Disabled"])
        cg_layout.addWidget(self.cb_conky, 2, 1)

        # Wallpaper
        cg_layout.addWidget(QLabel("Workstation Wallpaper:"), 2, 2)
        self.txt_wallpaper = QLineEdit(t.get("wallpaper", "/home/alpha/Pictures/victor-cyberpunk-wallpaper.png"))
        cg_layout.addWidget(self.txt_wallpaper, 2, 3)

        layout.addWidget(comp_group)

        # Color Pickers Grid
        colors_grid = QGridLayout()
        colors_grid.setSpacing(10)

        self.btn_col_bg = QPushButton(t.get("primary_bg", "#080C0B"))
        self.btn_col_bg.clicked.connect(lambda: self.pick_color(self.btn_col_bg))

        self.btn_col_subbg = QPushButton(t.get("secondary_bg", "#111820"))
        self.btn_col_subbg.clicked.connect(lambda: self.pick_color(self.btn_col_subbg))

        self.btn_col_accent = QPushButton(t.get("primary_accent", "#39FF88"))
        self.btn_col_accent.clicked.connect(lambda: self.pick_color(self.btn_col_accent))

        self.btn_col_cyan = QPushButton(t.get("secondary_accent", "#00D9FF"))
        self.btn_col_cyan.clicked.connect(lambda: self.pick_color(self.btn_col_cyan))

        colors_grid.addWidget(QLabel("Primary Background:"), 0, 0)
        colors_grid.addWidget(self.btn_col_bg, 0, 1)

        colors_grid.addWidget(QLabel("Secondary Background:"), 0, 2)
        colors_grid.addWidget(self.btn_col_subbg, 0, 3)

        colors_grid.addWidget(QLabel("Neon Green Accent:"), 1, 0)
        colors_grid.addWidget(self.btn_col_accent, 1, 1)

        colors_grid.addWidget(QLabel("Electric Cyan Accent:"), 1, 2)
        colors_grid.addWidget(self.btn_col_cyan, 1, 3)

        layout.addLayout(colors_grid)

        # Transparency Slider
        transp_box = QHBoxLayout()
        transp_box.addWidget(QLabel("HUD Panel Transparency:"))
        self.slider_transp = QSlider(Qt.Orientation.Horizontal)
        self.slider_transp.setRange(50, 100)
        self.slider_transp.setValue(int(t.get("panel_transparency", 88)))
        self.lbl_transp_val = QLabel(f"{t.get('panel_transparency', 88)}%")
        self.slider_transp.valueChanged.connect(lambda v: self.lbl_transp_val.setText(f"{v}%"))
        transp_box.addWidget(self.slider_transp)
        transp_box.addWidget(self.lbl_transp_val)
        layout.addLayout(transp_box)

        # Action Buttons
        btn_bar = QHBoxLayout()
        btn_reset_theme = QPushButton("Reset to Default Preset")
        btn_reset_theme.clicked.connect(self.reset_theme_defaults)

        btn_apply_theme = QPushButton("⚡ APPLY THEME TO ACTUAL KALI DESKTOP")
        btn_apply_theme.setObjectName("btnSavePrimary")
        btn_apply_theme.clicked.connect(self.save_theme_settings)

        btn_bar.addWidget(btn_reset_theme)
        btn_bar.addStretch()
        btn_bar.addWidget(btn_apply_theme)
        layout.addLayout(btn_bar)

    def on_preset_changed(self, preset_name: str):
        if preset_name in PRESET_PROFILES:
            p = PRESET_PROFILES[preset_name]
            self.btn_col_bg.setText(p["primary_bg"])
            self.btn_col_subbg.setText(p["secondary_bg"])
            self.btn_col_accent.setText(p["primary_accent"])
            self.btn_col_cyan.setText(p["secondary_accent"])
            self.txt_wallpaper.setText(p.get("wallpaper", ""))
            idx_icon = self.cb_icons.findText(p.get("icon_theme", ""))
            if idx_icon >= 0:
                self.cb_icons.setCurrentIndex(idx_icon)
            idx_xfwm = self.cb_xfwm.findText(p.get("xfwm_theme", ""))
            if idx_xfwm >= 0:
                self.cb_xfwm.setCurrentIndex(idx_xfwm)

    def pick_color(self, btn: QPushButton):
        curr = QColor(btn.text())
        col = QColorDialog.getColor(curr, self, "Pick Accent Color")
        if col.isValid():
            btn.setText(col.name())

    def reset_theme_defaults(self):
        self.cb_preset.setCurrentText("Cyberpunk Green")
        self.on_preset_changed("Cyberpunk Green")
        self.lbl_status.setText("Theme reset to Cyberpunk Green defaults.")

    def save_theme_settings(self, notify: bool = True):
        t = self.cfg.setdefault("theme", {})
        preset_name = self.cb_preset.currentText()
        t["preset"] = preset_name
        t["primary_bg"] = self.btn_col_bg.text()
        t["secondary_bg"] = self.btn_col_subbg.text()
        t["primary_accent"] = self.btn_col_accent.text()
        t["secondary_accent"] = self.btn_col_cyan.text()
        t["panel_transparency"] = self.slider_transp.value()
        t["wallpaper"] = self.txt_wallpaper.text()
        t["icon_theme"] = self.cb_icons.currentText()
        t["xfwm_theme"] = self.cb_xfwm.currentText()

        save_config(self.cfg, backup=True, label="theme_edit")

        custom_colors = {
            "primary_bg": t["primary_bg"],
            "secondary_bg": t["secondary_bg"],
            "primary_accent": t["primary_accent"],
            "secondary_accent": t["secondary_accent"],
            "icon_theme": t["icon_theme"],
            "xfwm_theme": t["xfwm_theme"],
            "wallpaper": t["wallpaper"]
        }

        # Apply to ACTUAL desktop environment (GTK, xfwm4, xfce4-panel, wallpaper, conky)
        apply_full_desktop_theme(preset_name, custom_colors)

        self.apply_theme()
        self.lbl_status.setText(f"Theme '{preset_name}' applied to ACTUAL Kali Linux desktop environment.")
        if notify:
            QMessageBox.information(
                self, "Desktop Theme Applied",
                f"Theme '{preset_name}' applied to the actual desktop:\n"
                f"• Top Navigation Panel transformed\n"
                f"• Bottom Application Dock active\n"
                f"• Window Manager theme: {t['xfwm_theme']}\n"
                f"• GTK3 CSS & Icons ({t['icon_theme']}) updated\n"
                f"• Conky system telemetry widget reloaded\n"
                f"• Wallpaper updated"
            )

    # -------------------------------------------------------------
    # TAB 7: BACKUPS & RESTORE
    # -------------------------------------------------------------
    def init_restore_tab(self):
        layout = QVBoxLayout(self.tab_restore)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Header Info Box
        info_card = QFrame()
        info_card.setObjectName("warningCard")
        ic_layout = QVBoxLayout(info_card)
        ic_lbl1 = QLabel("SAFETY & RECOVERY HUB")
        ic_lbl1.setObjectName("dangerHeading")
        ic_lbl2 = QLabel("Victor Command Center automatically creates timestamped backups before every modification.\nYou can revert configuration snapshots or restore the original factory Kali Linux desktop at any time.")
        ic_lbl2.setObjectName("dangerText")
        ic_layout.addWidget(ic_lbl1)
        ic_layout.addWidget(ic_lbl2)
        layout.addWidget(info_card)

        # Snapshot List
        layout.addWidget(QLabel("Configuration Backups & Snapshots:"))
        self.tbl_backups = QTableWidget()
        self.tbl_backups.setColumnCount(3)
        self.tbl_backups.setHorizontalHeaderLabels(["Snapshot File", "Creation Timestamp", "Size"])
        self.tbl_backups.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_backups.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_backups.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_backups.setObjectName("cyberTable")
        self.populate_backups_table()
        layout.addWidget(self.tbl_backups)

        # Snapshot Action Buttons
        snap_btn_bar = QHBoxLayout()
        btn_make_backup = QPushButton("+ Create Manual Backup Now")
        btn_make_backup.setObjectName("btnTabAction")
        btn_make_backup.clicked.connect(self.make_manual_backup)

        btn_restore_snap = QPushButton("↺ Restore Selected Snapshot")
        btn_restore_snap.setObjectName("btnTabAction")
        btn_restore_snap.clicked.connect(self.restore_selected_snapshot)

        snap_btn_bar.addWidget(btn_make_backup)
        snap_btn_bar.addWidget(btn_restore_snap)
        snap_btn_bar.addStretch()
        layout.addLayout(snap_btn_bar)

        # Desktop Restoration Section
        restore_box = QGroupBox("Factory Desktop Restoration Options")
        restore_box.setObjectName("restoreGroup")
        rb_layout = QVBoxLayout(restore_box)
        rb_layout.setSpacing(10)

        choice1_layout = QHBoxLayout()
        lbl_c1 = QLabel("Option 1: Restore Original Kali Desktop Settings (Retain Command Center)")
        lbl_c1.setObjectName("restoreOptionTitle")
        btn_c1 = QPushButton("Restore Original Desktop")
        btn_c1.setObjectName("btnDangerAction")
        btn_c1.clicked.connect(self.confirm_restore_desktop)
        choice1_layout.addWidget(lbl_c1)
        choice1_layout.addStretch()
        choice1_layout.addWidget(btn_c1)
        rb_layout.addLayout(choice1_layout)

        choice2_layout = QHBoxLayout()
        lbl_c2 = QLabel("Option 2: Completely Uninstall Command Center (Revert to stock Kali)")
        lbl_c2.setObjectName("restoreOptionTitle")
        btn_c2 = QPushButton("Complete Uninstall")
        btn_c2.setObjectName("btnDangerAction")
        btn_c2.clicked.connect(self.confirm_uninstall)
        choice2_layout.addWidget(lbl_c2)
        choice2_layout.addStretch()
        choice2_layout.addWidget(btn_c2)
        rb_layout.addLayout(choice2_layout)

        layout.addWidget(restore_box)

    def populate_backups_table(self):
        backups = list_backups()
        self.tbl_backups.setRowCount(len(backups))
        for r, b in enumerate(backups):
            self.tbl_backups.setItem(r, 0, QTableWidgetItem(b["filename"]))
            self.tbl_backups.setItem(r, 1, QTableWidgetItem(b["timestamp"]))
            self.tbl_backups.setItem(r, 2, QTableWidgetItem(f"{b['size_bytes']} B"))

    def make_manual_backup(self):
        b = create_backup(label="user_manual")
        self.populate_backups_table()
        self.lbl_status.setText(f"Manual snapshot created: {b.name}")
        QMessageBox.information(self, "Backup Created", f"Configuration snapshot created successfully:\n{b.name}")

    def restore_selected_snapshot(self):
        row = self.tbl_backups.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a snapshot from the table first.")
            return

        filename = self.tbl_backups.item(row, 0).text()
        confirm = QMessageBox.question(
            self, "Confirm Snapshot Revert",
            f"Are you sure you want to revert configuration to:\n{filename}?\n\nA safety snapshot of current settings will be taken first.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            target = Path.home() / ".config" / "victor-command-center" / "backups" / filename
            try:
                restore_backup(target)
                self.cfg = load_config()
                self.populate_skills_table()
                self.populate_projects_table()
                self.populate_learning_table()
                self.populate_backups_table()
                self.apply_theme()
                QMessageBox.information(self, "Restore Successful", f"Restored configuration from {filename}.")
            except Exception as e:
                QMessageBox.critical(self, "Restore Failed", f"Error restoring backup: {e}")

    def confirm_restore_desktop(self):
        confirm = QMessageBox.question(
            self, "Confirm Factory Desktop Restore",
            "This will restore your original Kali Linux desktop theme (Kali-Slate-Dark), original icons, original panels, and original terminal configuration.\n\nYour personal files and projects will NOT be affected.\n\nProceed with factory desktop restore?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            success = restore_factory_desktop()
            if success:
                QMessageBox.information(self, "Desktop Restored", "Original Kali desktop settings restored from factory baseline.\nLog out and back in or restart XFCE panel to view stock desktop.")
            else:
                QMessageBox.critical(self, "Restore Error", "Could not restore all baseline desktop files. Check docs/RESTORE_GUIDE.md.")

    def confirm_uninstall(self):
        confirm = QMessageBox.question(
            self, "Confirm Complete Uninstall",
            "This will restore original desktop settings AND remove Victor Command Center launchers from your Desktop and application menu.\n\nProceed with uninstallation?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            uninstall_command_center()
            QMessageBox.information(self, "Uninstalled", "Victor Command Center desktop integrations removed.\nOriginal desktop restored.")
            self.close()

    # -------------------------------------------------------------
    # GLOBAL ACTIONS & THEME STYLESHEET
    # -------------------------------------------------------------
    def save_all_settings(self):
        self.save_profile_data()
        self.save_skills_data()
        self.save_projects_data()
        self.save_learning_data()
        self.save_startup_settings(notify=False)
        self.save_theme_settings(notify=False)
        self.lbl_status.setText("All workstation settings atomically saved & synchronized.")
        QMessageBox.information(self, "Saved", "All Victor Command Center settings successfully saved.")

    def launch_hud(self):
        hud_script = Path(__file__).resolve().parent / "hud.py"
        subprocess.Popen(["python3", str(hud_script)])

    def apply_theme(self):
        t = self.cfg.get("theme", {})
        accent = t.get("primary_accent", "#00ff66")
        cyan = t.get("secondary_accent", "#00e5ff")
        bg = t.get("primary_bg", "#0a0b10")
        sub_bg = t.get("secondary_bg", "#12161f")
        text = t.get("text_color", "#e0f8ff")

        style = f"""
        QWidget {{
            background-color: {bg};
            color: {text};
            font-family: 'FiraCode', 'Monospace', monospace;
            font-size: 11px;
        }}
        #appHeader {{
            background-color: {sub_bg};
            border: 1px solid rgba(0, 229, 255, 0.35);
            border-left: 4px solid {accent};
            border-radius: 5px;
        }}
        #appHeaderTitle {{
            color: {accent};
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 1.5px;
        }}
        #appHeaderSubtitle {{
            color: {cyan};
            font-size: 10px;
            letter-spacing: 0.5px;
        }}
        #btnCyberHeader {{
            background-color: rgba(0, 255, 102, 0.12);
            color: {accent};
            border: 1px solid {accent};
            border-radius: 4px;
            padding: 6px 14px;
            font-weight: bold;
        }}
        #btnCyberHeader:hover {{
            background-color: {accent};
            color: #000;
        }}
        QTabWidget::pane {{
            border: 1px solid rgba(0, 229, 255, 0.3);
            background-color: rgba(14, 18, 26, 0.95);
            border-radius: 4px;
        }}
        QTabBar::tab {{
            background-color: #0e121a;
            color: #94a3b8;
            padding: 8px 18px;
            border: 1px solid #1e293b;
            border-bottom: none;
            margin-right: 2px;
            font-weight: bold;
            font-size: 10px;
        }}
        QTabBar::tab:selected {{
            color: {accent};
            border: 1px solid {accent};
            border-bottom: 2px solid {accent};
            background-color: rgba(0, 255, 102, 0.1);
        }}
        QLineEdit, QTextEdit, QSpinBox, QComboBox {{
            background-color: #0b0e14;
            color: #ffffff;
            border: 1px solid #1e293b;
            border-radius: 3px;
            padding: 6px;
        }}
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border: 1px solid {cyan};
        }}
        #cyberTable, #cyberList {{
            background-color: #090c12;
            color: {text};
            border: 1px solid #1e293b;
            gridline-color: #141b26;
            border-radius: 4px;
        }}
        QHeaderView::section {{
            background-color: {sub_bg};
            color: {cyan};
            border: 1px solid #1e293b;
            padding: 6px;
            font-weight: bold;
        }}
        #btnTabAction {{
            background-color: rgba(0, 229, 255, 0.15);
            color: {cyan};
            border: 1px solid {cyan};
            border-radius: 4px;
            padding: 6px 14px;
            font-weight: bold;
        }}
        #btnTabAction:hover {{
            background-color: {cyan};
            color: #000;
        }}
        #btnDangerAction {{
            background-color: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border: 1px solid #ef4444;
            border-radius: 4px;
            padding: 6px 14px;
            font-weight: bold;
        }}
        #btnDangerAction:hover {{
            background-color: #ef4444;
            color: #fff;
        }}
        #btnSavePrimary {{
            background-color: {accent};
            color: #000;
            border: none;
            border-radius: 4px;
            padding: 8px 20px;
            font-weight: bold;
            font-size: 11px;
        }}
        #btnSavePrimary:hover {{
            background-color: #39ff88;
        }}
        #btnPreviewCyber {{
            background-color: rgba(0, 255, 102, 0.2);
            color: {accent};
            border: 1px solid {accent};
            border-radius: 4px;
            padding: 6px 14px;
            font-weight: bold;
        }}
        #btnPreviewCyber:hover {{
            background-color: {accent};
            color: #000;
        }}
        #warningCard {{
            background-color: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(0, 229, 255, 0.3);
            border-left: 4px solid {cyan};
            border-radius: 4px;
            padding: 10px;
        }}
        #dangerHeading {{
            color: {cyan};
            font-size: 12px;
            font-weight: bold;
        }}
        #dangerText {{
            color: #94a3b8;
            font-size: 10px;
        }}
        #restoreGroup {{
            border: 1px solid #334155;
            border-radius: 4px;
            margin-top: 10px;
            font-weight: bold;
            color: #cbd5e1;
            padding: 10px;
        }}
        #restoreOptionTitle {{
            color: #e2e8f0;
            font-size: 11px;
        }}
        #footerStatus {{
            color: #64748b;
            font-size: 10px;
        }}
        QProgressBar {{
            background-color: #090c12;
            border: 1px solid #1e293b;
            border-radius: 3px;
            height: 16px;
            text-align: center;
            color: #fff;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {cyan}, stop:1 {accent});
            border-radius: 2px;
        }}
        #themePreviewBox {{
            background-color: {sub_bg};
            border: 1px solid rgba(0, 229, 255, 0.3);
            border-radius: 4px;
            padding: 12px;
        }}
        #previewTitle {{
            color: {cyan};
            font-weight: bold;
            font-size: 11px;
        }}
        #btnPreviewPrimary {{
            background-color: {accent};
            color: #000;
            border: none;
            border-radius: 3px;
            padding: 6px;
            font-weight: bold;
        }}
        #btnPreviewSecondary {{
            background-color: transparent;
            color: {cyan};
            border: 1px solid {cyan};
            border-radius: 3px;
            padding: 6px;
        }}
        """
        self.setStyleSheet(style)


def main():
    app = QApplication(sys.argv)
    window = VictorCommandCenter()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
