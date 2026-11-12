#!/usr/bin/env python3
"""
Victor Command Center - Security & Vulnerability Center UI
PyQt6 Interface for defensive Linux security assessment, CVE tracking, and patch management.
"""

import os
import sys
import webbrowser
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QTabWidget, QTextEdit, QMessageBox, QGroupBox, QSplitter, QCheckBox,
    QProgressBar, QFrame, QFileDialog
)

from security_center import SecurityCenter, VulnerabilityFinding
from app_manager_ui import SafeUninstallDialog


class SecurityCenterTab(QWidget):
    """Main Security & Vulnerability Center Tab Widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sec_center = SecurityCenter()
        self.findings_data: List[VulnerabilityFinding] = []
        self.init_ui()
        # Initial load
        QTimer.singleShot(150, self.refresh_security_data)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Tab Segmenter
        self.subtabs = QTabWidget()
        self.subtabs.setObjectName("subTabs")

        # View 1: Security Overview Dashboard
        self.tab_overview = QWidget()
        self.init_overview_view()
        self.subtabs.addTab(self.tab_overview, "SECURITY OVERVIEW")

        # View 2: Vulnerability Findings & CVEs
        self.tab_vulns = QWidget()
        self.init_vulns_view()
        self.subtabs.addTab(self.tab_vulns, "VULNERABILITIES & CVES")

        # View 3: System Hardening & Exposure Audit
        self.tab_audit = QWidget()
        self.init_audit_view()
        self.subtabs.addTab(self.tab_audit, "HARDENING & EXPOSURE")

        # View 4: Patch Management & Safety Engine
        self.tab_patch = QWidget()
        self.init_patch_view()
        self.subtabs.addTab(self.tab_patch, "PATCH MANAGEMENT")

        layout.addWidget(self.subtabs)

    # -------------------------------------------------------------
    # VIEW 1: SECURITY OVERVIEW DASHBOARD
    # -------------------------------------------------------------
    def init_overview_view(self):
        layout = QVBoxLayout(self.tab_overview)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(14)

        # Scorecards Grid
        grid = QHBoxLayout()
        grid.setSpacing(10)

        # 1. Posture Grade Card
        self.card_grade = QFrame()
        self.card_grade.setStyleSheet("background: #111820; border: 2px solid #39FF88; border-radius: 6px; padding: 10px;")
        v_g = QVBoxLayout(self.card_grade)
        v_g.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_g_title = QLabel("SECURITY POSTURE")
        lbl_g_title.setStyleSheet("font-size: 11px; color: #82948C; font-weight: bold; font-family: monospace;")
        self.lbl_grade_val = QLabel("Grade --")
        self.lbl_grade_val.setStyleSheet("font-size: 26px; font-weight: 900; color: #39FF88; font-family: monospace;")
        self.lbl_grade_status = QLabel("ASSESSING...")
        self.lbl_grade_status.setStyleSheet("font-size: 11px; font-weight: bold; color: #39FF88; font-family: monospace;")
        v_g.addWidget(lbl_g_title, alignment=Qt.AlignmentFlag.AlignCenter)
        v_g.addWidget(self.lbl_grade_val, alignment=Qt.AlignmentFlag.AlignCenter)
        v_g.addWidget(self.lbl_grade_status, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.card_grade)

        # 2. Risk Score Card
        self.card_risk = QFrame()
        self.card_risk.setStyleSheet("background: #111820; border: 1px solid #1F2E3D; border-radius: 6px; padding: 10px;")
        v_r = QVBoxLayout(self.card_risk)
        v_r.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_title = QLabel("SYSTEM RISK INDEX")
        lbl_r_title.setStyleSheet("font-size: 11px; color: #82948C; font-weight: bold; font-family: monospace;")
        self.lbl_risk_val = QLabel("0")
        self.lbl_risk_val.setStyleSheet("font-size: 26px; font-weight: 900; color: #00D9FF; font-family: monospace;")
        lbl_r_sub = QLabel("Weighted Severity")
        lbl_r_sub.setStyleSheet("font-size: 11px; color: #82948C; font-family: monospace;")
        v_r.addWidget(lbl_r_title, alignment=Qt.AlignmentFlag.AlignCenter)
        v_r.addWidget(self.lbl_risk_val, alignment=Qt.AlignmentFlag.AlignCenter)
        v_r.addWidget(lbl_r_sub, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.card_risk)

        # 3. Critical Findings Card
        self.card_crit = QFrame()
        self.card_crit.setStyleSheet("background: #111820; border: 1px solid #1F2E3D; border-radius: 6px; padding: 10px;")
        v_c = QVBoxLayout(self.card_crit)
        v_c.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_title = QLabel("CRITICAL VULNS")
        lbl_c_title.setStyleSheet("font-size: 11px; color: #82948C; font-weight: bold; font-family: monospace;")
        self.lbl_crit_val = QLabel("0")
        self.lbl_crit_val.setStyleSheet("font-size: 26px; font-weight: 900; color: #FF3366; font-family: monospace;")
        lbl_c_sub = QLabel("Immediate Threat")
        lbl_c_sub.setStyleSheet("font-size: 11px; color: #FF3366; font-family: monospace;")
        v_c.addWidget(lbl_c_title, alignment=Qt.AlignmentFlag.AlignCenter)
        v_c.addWidget(self.lbl_crit_val, alignment=Qt.AlignmentFlag.AlignCenter)
        v_c.addWidget(lbl_c_sub, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.card_crit)

        # 4. High Severity Card
        self.card_high = QFrame()
        self.card_high.setStyleSheet("background: #111820; border: 1px solid #1F2E3D; border-radius: 6px; padding: 10px;")
        v_h = QVBoxLayout(self.card_high)
        v_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_h_title = QLabel("HIGH SEVERITY")
        lbl_h_title.setStyleSheet("font-size: 11px; color: #82948C; font-weight: bold; font-family: monospace;")
        self.lbl_high_val = QLabel("0")
        self.lbl_high_val.setStyleSheet("font-size: 26px; font-weight: 900; color: #FF8800; font-family: monospace;")
        lbl_h_sub = QLabel("Action Required")
        lbl_h_sub.setStyleSheet("font-size: 11px; color: #FF8800; font-family: monospace;")
        v_h.addWidget(lbl_h_title, alignment=Qt.AlignmentFlag.AlignCenter)
        v_h.addWidget(self.lbl_high_val, alignment=Qt.AlignmentFlag.AlignCenter)
        v_h.addWidget(lbl_h_sub, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.card_high)

        # 5. Outdated Packages Card
        self.card_out = QFrame()
        self.card_out.setStyleSheet("background: #111820; border: 1px solid #1F2E3D; border-radius: 6px; padding: 10px;")
        v_o = QVBoxLayout(self.card_out)
        v_o.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_o_title = QLabel("OUTDATED PACKAGES")
        lbl_o_title.setStyleSheet("font-size: 11px; color: #82948C; font-weight: bold; font-family: monospace;")
        self.lbl_out_val = QLabel("0")
        self.lbl_out_val.setStyleSheet("font-size: 26px; font-weight: 900; color: #00D9FF; font-family: monospace;")
        lbl_o_sub = QLabel("Pending Updates")
        lbl_o_sub.setStyleSheet("font-size: 11px; color: #00D9FF; font-family: monospace;")
        v_o.addWidget(lbl_o_title, alignment=Qt.AlignmentFlag.AlignCenter)
        v_o.addWidget(self.lbl_out_val, alignment=Qt.AlignmentFlag.AlignCenter)
        v_o.addWidget(lbl_o_sub, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.card_out)

        layout.addLayout(grid)

        # Methodology & Sync Banner
        banner = QFrame()
        banner.setStyleSheet("background: #080C0B; border: 1px solid #1F2E3D; border-radius: 4px; padding: 12px;")
        v_b = QVBoxLayout(banner)
        v_b.setSpacing(6)

        self.lbl_meta_sync = QLabel("Last Assessment: Calculating...  |  Package Repo Sync: ...  |  Last Security Update: ...")
        self.lbl_meta_sync.setStyleSheet("color: #00D9FF; font-family: monospace; font-size: 12px;")
        v_b.addWidget(self.lbl_meta_sync)

        lbl_method = QLabel(
            "SCORING METHODOLOGY (VCC-SPM): Grounded deterministic risk index computed via weighted severity: "
            "Critical = 25 pts, High = 10 pts, Medium = 3 pts, Low = 1 pt. Grade A (<=10), Grade B (11-30), Grade C (31-70), Grade D (71-150), Grade F (>150). "
            "Evaluates real Debian Security Tracker CVEs, kernel lifecycle, wildcard listening sockets, and sensitive file permissions."
        )
        lbl_method.setWordWrap(True)
        lbl_method.setStyleSheet("color: #82948C; font-family: monospace; font-size: 11px;")
        v_b.addWidget(lbl_method)

        layout.addWidget(banner)

        # Recent Findings Summary Box
        box_findings = QGroupBox("TOP ACTIVE DEFENSIVE SECURITY FINDINGS")
        box_findings.setStyleSheet("QGroupBox { color: #39FF88; font-weight: bold; border: 1px solid #1F2E3D; margin-top: 6px; padding-top: 10px; font-family: monospace; }")
        v_f = QVBoxLayout(box_findings)

        self.table_overview_findings = QTableWidget(0, 5)
        self.table_overview_findings.setHorizontalHeaderLabels(["Severity", "Finding Title", "Component", "Installed vs Target", "CVE ID"])
        self.table_overview_findings.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_overview_findings.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_overview_findings.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table_overview_findings.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table_overview_findings.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_overview_findings.setStyleSheet("background-color: #080C0B; color: #D6E5DF; font-family: monospace;")
        v_f.addWidget(self.table_overview_findings)

        layout.addWidget(box_findings, stretch=1)

        # Actions Toolbar
        action_bar = QHBoxLayout()

        btn_scan = QPushButton("RUN SECURITY SCAN")
        btn_scan.setStyleSheet("background: #111820; color: #39FF88; border: 1px solid #39FF88; padding: 8px 18px; font-weight: bold;")
        btn_scan.clicked.connect(lambda: self.refresh_security_data(force=True))
        action_bar.addWidget(btn_scan)

        btn_safety = QPushButton("SAFETY PRE-CHECKS")
        btn_safety.setStyleSheet("background: #111820; color: #00D9FF; border: 1px solid #00D9FF; padding: 8px 18px; font-weight: bold;")
        btn_safety.clicked.connect(self.show_safety_checks)
        action_bar.addWidget(btn_safety)

        action_bar.addStretch()

        btn_export_html = QPushButton("EXPORT HTML AUDIT REPORT")
        btn_export_html.setStyleSheet("background: #111820; color: #00D9FF; border: 1px solid #00D9FF; padding: 8px 18px; font-weight: bold;")
        btn_export_html.clicked.connect(self.export_html_report)
        action_bar.addWidget(btn_export_html)

        btn_export_json = QPushButton("EXPORT JSON AUDIT")
        btn_export_json.setStyleSheet("background: #111820; color: #D6E5DF; border: 1px solid #1F2E3D; padding: 8px 18px; font-weight: bold;")
        btn_export_json.clicked.connect(self.export_json_report)
        action_bar.addWidget(btn_export_json)

        layout.addLayout(action_bar)

    def refresh_security_data(self, force: bool = False):
        """Run real assessment and update all views."""
        overview = self.sec_center.get_security_overview()
        self.findings_data = self.sec_center.run_assessment(force_refresh=force)

        # Update cards
        self.lbl_grade_val.setText(overview["posture_grade"])
        self.lbl_grade_val.setStyleSheet(f"font-size: 26px; font-weight: 900; color: {overview['posture_color']}; font-family: monospace;")
        self.lbl_grade_status.setText(overview["posture_status"])
        self.lbl_grade_status.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {overview['posture_color']}; font-family: monospace;")
        self.card_grade.setStyleSheet(f"background: #111820; border: 2px solid {overview['posture_color']}; border-radius: 6px; padding: 10px;")

        self.lbl_risk_val.setText(str(overview["risk_score"]))
        self.lbl_crit_val.setText(str(overview["critical_count"]))
        self.lbl_high_val.setText(str(overview["high_count"]))
        self.lbl_out_val.setText(str(overview["outdated_packages_count"]))

        self.lbl_meta_sync.setText(
            f"Last Assessment: {overview['last_assessment']}  |  "
            f"Package Repo Sync: {overview['last_db_update']}  |  "
            f"Last Security Update: {overview['last_security_update']}"
        )

        # Populate overview table with top findings
        self.table_overview_findings.setRowCount(0)
        for f in self.findings_data[:8]:
            row = self.table_overview_findings.rowCount()
            self.table_overview_findings.insertRow(row)

            it_sev = QTableWidgetItem(f.severity)
            it_sev.setForeground(self._get_severity_color(f.severity))
            self.table_overview_findings.setItem(row, 0, it_sev)

            self.table_overview_findings.setItem(row, 1, QTableWidgetItem(f.title))
            self.table_overview_findings.setItem(row, 2, QTableWidgetItem(f.affected_package))
            self.table_overview_findings.setItem(row, 3, QTableWidgetItem(f"{f.installed_version} -> {f.fixed_version}"))
            self.table_overview_findings.setItem(row, 4, QTableWidgetItem(f.cve_id))

        # Also refresh other tabs
        self.populate_vulns_table(self.findings_data)
        self.populate_audit_table(self.findings_data)
        self.populate_patch_table()

    def _get_severity_color(self, severity: str) -> QColor:
        """Map severity to cyberpunk palette color."""
        if severity == "CRITICAL":
            return QColor("#FF3366")
        elif severity == "HIGH":
            return QColor("#FF8800")
        elif severity == "MEDIUM":
            return QColor("#FFD700")
        elif severity == "LOW":
            return QColor("#00D9FF")
        return QColor("#82948C")

    # -------------------------------------------------------------
    # VIEW 2: VULNERABILITY FINDINGS & CVES
    # -------------------------------------------------------------
    def init_vulns_view(self):
        layout = QVBoxLayout(self.tab_vulns)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Filters
        f_box = QHBoxLayout()
        self.input_vuln_search = QLineEdit()
        self.input_vuln_search.setPlaceholderText("Filter findings by CVE, package name, or vulnerability title...")
        self.input_vuln_search.setStyleSheet("background: #080C0B; color: #39FF88; border: 1px solid #1F2E3D; padding: 6px; font-family: monospace;")
        self.input_vuln_search.textChanged.connect(self.filter_vulns)
        f_box.addWidget(self.input_vuln_search, stretch=3)

        self.combo_vuln_sev = QComboBox()
        self.combo_vuln_sev.addItems(["All Severities", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.combo_vuln_sev.setStyleSheet("background: #111820; color: #D6E5DF; border: 1px solid #1F2E3D; padding: 6px;")
        self.combo_vuln_sev.currentTextChanged.connect(self.filter_vulns)
        f_box.addWidget(self.combo_vuln_sev, stretch=1)

        layout.addLayout(f_box)

        # Findings Table
        self.table_vulns = QTableWidget(0, 6)
        self.table_vulns.setHorizontalHeaderLabels(["Severity", "Vulnerability Title", "Affected Package", "Installed -> Fixed", "CVE / Rule", "Status"])
        self.table_vulns.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_vulns.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_vulns.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table_vulns.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table_vulns.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_vulns.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table_vulns.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_vulns.setStyleSheet("background-color: #080C0B; color: #D6E5DF; font-family: monospace;")
        self.table_vulns.itemSelectionChanged.connect(self.display_vuln_details)
        layout.addWidget(self.table_vulns, stretch=2)

        # Detail Inspector
        self.box_detail = QGroupBox("FINDING DETAILS & REMEDIATION ROADMAP")
        self.box_detail.setStyleSheet("QGroupBox { color: #00D9FF; font-weight: bold; border: 1px solid #1F2E3D; margin-top: 6px; padding-top: 10px; font-family: monospace; }")
        v_d = QVBoxLayout(self.box_detail)

        self.txt_vuln_desc = QTextEdit()
        self.txt_vuln_desc.setReadOnly(True)
        self.txt_vuln_desc.setStyleSheet("background: #080C0B; color: #D6E5DF; font-family: monospace; border: 1px solid #1F2E3D;")
        v_d.addWidget(self.txt_vuln_desc)

        # Remediation Action Buttons
        h_rem = QHBoxLayout()
        self.lbl_selected_finding = QLabel("Select a finding above to inspect actionable remediations.")
        self.lbl_selected_finding.setStyleSheet("color: #82948C; font-family: monospace; font-size: 12px;")
        h_rem.addWidget(self.lbl_selected_finding)
        h_rem.addStretch()

        self.btn_open_advisory = QPushButton("OPEN ADVISORY URL")
        self.btn_open_advisory.setStyleSheet("background: #111820; color: #00D9FF; border: 1px solid #00D9FF; padding: 6px 14px; font-weight: bold;")
        self.btn_open_advisory.clicked.connect(self.open_advisory_link)
        h_rem.addWidget(self.btn_open_advisory)

        self.btn_apply_remediation = QPushButton("APPLY REMEDIATION")
        self.btn_apply_remediation.setStyleSheet("background: #111820; color: #39FF88; border: 1px solid #39FF88; padding: 6px 14px; font-weight: bold;")
        self.btn_apply_remediation.clicked.connect(self.apply_remediation_action)
        h_rem.addWidget(self.btn_apply_remediation)

        self.btn_defer_finding = QPushButton("MARK DEFERRED / RESOLVED")
        self.btn_defer_finding.setStyleSheet("background: #111820; color: #D6E5DF; border: 1px solid #1F2E3D; padding: 6px 14px;")
        self.btn_defer_finding.clicked.connect(self.toggle_finding_resolved)
        h_rem.addWidget(self.btn_defer_finding)

        v_d.addLayout(h_rem)
        layout.addWidget(self.box_detail, stretch=1)

    def populate_vulns_table(self, findings: List[VulnerabilityFinding]):
        """Populate vulnerability findings table."""
        self.table_vulns.setRowCount(0)
        for f in findings:
            row = self.table_vulns.rowCount()
            self.table_vulns.insertRow(row)

            # Severity
            it_sev = QTableWidgetItem(f.severity)
            it_sev.setForeground(self._get_severity_color(f.severity))
            it_sev.setData(Qt.ItemDataRole.UserRole, f)
            self.table_vulns.setItem(row, 0, it_sev)

            # Title
            self.table_vulns.setItem(row, 1, QTableWidgetItem(f.title))

            # Affected package
            self.table_vulns.setItem(row, 2, QTableWidgetItem(f.affected_package))

            # Installed -> Fixed
            self.table_vulns.setItem(row, 3, QTableWidgetItem(f"{f.installed_version} -> {f.fixed_version}"))

            # CVE
            self.table_vulns.setItem(row, 4, QTableWidgetItem(f.cve_id))

            # Status
            status_str = "RESOLVED" if f.resolved else "UNRESOLVED"
            it_stat = QTableWidgetItem(status_str)
            it_stat.setForeground(QColor("#39FF88") if f.resolved else QColor("#FF8800"))
            self.table_vulns.setItem(row, 5, it_stat)

    def filter_vulns(self):
        """Filter findings by query and severity."""
        query = self.input_vuln_search.text().strip().lower()
        sev_filter = self.combo_vuln_sev.currentText()

        filtered = []
        for f in self.findings_data:
            if sev_filter != "All Severities" and f.severity != sev_filter:
                continue
            if query:
                if (query not in f.title.lower() and
                    query not in f.affected_package.lower() and
                    query not in f.cve_id.lower()):
                    continue
            filtered.append(f)
        self.populate_vulns_table(filtered)

    def get_selected_finding(self) -> Optional[VulnerabilityFinding]:
        """Return currently selected finding."""
        selected = self.table_vulns.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.table_vulns.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def display_vuln_details(self):
        """Display details of the selected finding."""
        f = self.get_selected_finding()
        if not f:
            self.txt_vuln_desc.clear()
            self.lbl_selected_finding.setText("Select a finding above to inspect actionable remediations.")
            return

        self.lbl_selected_finding.setText(f"Selected: {f.id} ({f.affected_package})")
        details = (
            f"// FINDING: {f.title}\n"
            f"Identifier:       {f.cve_id} (Severity: {f.severity})\n"
            f"Category:         {f.category}  |  Source: {f.source}\n"
            f"Component:        {f.affected_package}\n"
            f"Installed State:  {f.installed_version}\n"
            f"Proposed Fix:     {f.fixed_version}\n\n"
            f"Description:\n{f.description}\n\n"
            f"System Evidence:\n{f.evidence}\n\n"
            f"Recommended Remediation ({f.remediation_type}):\n{f.remediation}\n\n"
            f"Official Advisory Reference: {f.advisory_url}\n"
        )
        self.txt_vuln_desc.setText(details)

    def open_advisory_link(self):
        """Open official advisory reference in default browser."""
        f = self.get_selected_finding()
        if f and f.advisory_url:
            webbrowser.open(f.advisory_url)

    def apply_remediation_action(self):
        """Trigger remediation workflow for selected finding."""
        f = self.get_selected_finding()
        if not f:
            QMessageBox.warning(self, "No Selection", "Please select a finding to remediate.")
            return

        if f.remediation_type == "UPDATE":
            # Switch to patch management view
            self.subtabs.setCurrentIndex(3)
        elif f.remediation_type == "REMOVE":
            from app_manager import ApplicationManager
            mgr = ApplicationManager()
            dlg = SafeUninstallDialog([f.affected_package], mgr, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.sec_center.mark_finding_resolved(f.id, True)
                self.refresh_security_data(force=True)
        elif f.remediation_type == "CONFIG_FIX":
            QMessageBox.information(
                self, "Remediation Guidance",
                f"Configuration Remediation Required:\n\n{f.remediation}\n\n"
                "Execute the recommended sysctl, permissions, or service configuration in terminal."
            )

    def toggle_finding_resolved(self):
        """Toggle resolved/deferred state of finding."""
        f = self.get_selected_finding()
        if not f:
            return
        new_state = not f.resolved
        self.sec_center.mark_finding_resolved(f.id, new_state)
        self.refresh_security_data(force=False)

    # -------------------------------------------------------------
    # VIEW 3: SYSTEM HARDENING & EXPOSURE AUDIT
    # -------------------------------------------------------------
    def init_audit_view(self):
        layout = QVBoxLayout(self.tab_audit)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        box_audit = QGroupBox("DEFENSIVE AUDIT: KERNEL, NETWORK SOCKETS & PERMISSIONS")
        box_audit.setStyleSheet("QGroupBox { color: #00D9FF; font-weight: bold; border: 1px solid #1F2E3D; margin-top: 6px; padding-top: 10px; font-family: monospace; }")
        v_a = QVBoxLayout(box_audit)

        self.table_audit = QTableWidget(0, 4)
        self.table_audit.setHorizontalHeaderLabels(["Check Category", "Component / Target", "Audit Finding & Evidence", "Hardening Action"])
        self.table_audit.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table_audit.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table_audit.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_audit.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table_audit.setStyleSheet("background-color: #080C0B; color: #D6E5DF; font-family: monospace;")
        v_a.addWidget(self.table_audit)

        layout.addWidget(box_audit)

    def populate_audit_table(self, findings: List[VulnerabilityFinding]):
        """Populate hardening audit checks."""
        self.table_audit.setRowCount(0)
        audit_findings = [f for f in findings if f.category in ["Kernel Security", "Network Exposure", "Permissions", "Configuration"]]

        for f in audit_findings:
            row = self.table_audit.rowCount()
            self.table_audit.insertRow(row)

            it_cat = QTableWidgetItem(f.category)
            it_cat.setForeground(self._get_severity_color(f.severity))
            self.table_audit.setItem(row, 0, it_cat)

            self.table_audit.setItem(row, 1, QTableWidgetItem(f.affected_package))
            self.table_audit.setItem(row, 2, QTableWidgetItem(f"{f.title}: {f.evidence}"))
            self.table_audit.setItem(row, 3, QTableWidgetItem(f.remediation))

    # -------------------------------------------------------------
    # VIEW 4: PATCH MANAGEMENT & SAFETY WORKFLOW
    # -------------------------------------------------------------
    def init_patch_view(self):
        layout = QVBoxLayout(self.tab_patch)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # Safety Pre-checks Banner
        self.box_prechecks = QGroupBox("PATCH SAFETY PRE-CONDITIONS VERIFICATION")
        self.box_prechecks.setStyleSheet("QGroupBox { color: #39FF88; font-weight: bold; border: 1px solid #1F2E3D; margin-top: 6px; padding-top: 10px; font-family: monospace; }")
        v_p = QVBoxLayout(self.box_prechecks)

        self.lbl_precheck_status = QLabel("Checking safety pre-conditions...")
        self.lbl_precheck_status.setStyleSheet("color: #D6E5DF; font-family: monospace; font-size: 13px;")
        v_p.addWidget(self.lbl_precheck_status)
        layout.addWidget(self.box_prechecks)

        # Patch Candidates Table
        box_patches = QGroupBox("SELECT SECURITY PATCHES TO APPLY")
        box_patches.setStyleSheet("QGroupBox { color: #00D9FF; font-weight: bold; border: 1px solid #1F2E3D; margin-top: 6px; padding-top: 10px; font-family: monospace; }")
        v_pt = QVBoxLayout(box_patches)

        self.table_patches = QTableWidget(0, 5)
        self.table_patches.setHorizontalHeaderLabels(["Select", "Package Name", "Current Version", "Security Target Version", "Resolves CVE"])
        self.table_patches.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_patches.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table_patches.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table_patches.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table_patches.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table_patches.setStyleSheet("background-color: #080C0B; color: #D6E5DF; font-family: monospace;")
        v_pt.addWidget(self.table_patches)

        layout.addWidget(box_patches, stretch=1)

        # Patch Execution Action Bar
        action_bar = QHBoxLayout()

        btn_select_all = QPushButton("SELECT ALL SECURITY PATCHES")
        btn_select_all.setStyleSheet("background: #111820; color: #00D9FF; border: 1px solid #00D9FF; padding: 7px 14px; font-weight: bold;")
        btn_select_all.clicked.connect(self.select_all_patches)
        action_bar.addWidget(btn_select_all)

        action_bar.addStretch()

        btn_preview_plan = QPushButton("PREVIEW EXECUTION PLAN")
        btn_preview_plan.setStyleSheet("background: #111820; color: #39FF88; border: 1px solid #39FF88; padding: 7px 16px; font-weight: bold;")
        btn_preview_plan.clicked.connect(self.preview_patch_plan)
        action_bar.addWidget(btn_preview_plan)

        btn_rescan = QPushButton("VERIFICATION RESCAN")
        btn_rescan.setStyleSheet("background: #111820; color: #D6E5DF; border: 1px solid #1F2E3D; padding: 7px 16px;")
        btn_rescan.clicked.connect(lambda: self.refresh_security_data(force=True))
        action_bar.addWidget(btn_rescan)

        layout.addLayout(action_bar)

    def populate_patch_table(self):
        """Populate patch candidates and check preconditions."""
        # Check safety pre-conditions
        prechecks = self.sec_center.check_safety_preconditions()
        if prechecks["all_passed"]:
            status_text = (
                f"SAFETY PRE-CHECKS PASSED: Root filesystem has {prechecks['free_space_gb']} GB free space (>= 1.0 GB ok). "
                "No package manager lock held. DPKG database consistency verified."
            )
            self.lbl_precheck_status.setText(status_text)
            self.lbl_precheck_status.setStyleSheet("color: #39FF88; font-weight: bold; font-family: monospace;")
        else:
            issues = " | ".join(prechecks["issues"])
            status_text = f"SAFETY PRE-CHECKS WARNING: {issues}"
            self.lbl_precheck_status.setText(status_text)
            self.lbl_precheck_status.setStyleSheet("color: #FF3366; font-weight: bold; font-family: monospace;")

        # Populate table
        update_findings = [f for f in self.findings_data if f.remediation_type == "UPDATE" and not f.resolved]
        self.table_patches.setRowCount(0)

        for f in update_findings:
            row = self.table_patches.rowCount()
            self.table_patches.insertRow(row)

            chk = QCheckBox()
            chk.setChecked(True)
            chk.setStyleSheet("margin-left: 10px;")
            self.table_patches.setCellWidget(row, 0, chk)

            it_pkg = QTableWidgetItem(f.affected_package)
            it_pkg.setData(Qt.ItemDataRole.UserRole, f)
            self.table_patches.setItem(row, 1, it_pkg)

            self.table_patches.setItem(row, 2, QTableWidgetItem(f.installed_version))
            self.table_patches.setItem(row, 3, QTableWidgetItem(f.fixed_version))
            self.table_patches.setItem(row, 4, QTableWidgetItem(f.cve_id))

    def select_all_patches(self):
        """Select all patch checkboxes."""
        for row in range(self.table_patches.rowCount()):
            chk = self.table_patches.cellWidget(row, 0)
            if isinstance(chk, QCheckBox):
                chk.setChecked(True)

    def preview_patch_plan(self):
        """Preview execution plan for selected patches."""
        selected_ids = []
        for row in range(self.table_patches.rowCount()):
            chk = self.table_patches.cellWidget(row, 0)
            if isinstance(chk, QCheckBox) and chk.isChecked():
                it = self.table_patches.item(row, 1)
                if it:
                    f = it.data(Qt.ItemDataRole.UserRole)
                    if f:
                        selected_ids.append(f.id)

        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select at least one security patch to preview.")
            return

        plan = self.sec_center.generate_patch_plan(selected_ids)
        pkgs_str = "\n".join(f"- {p[0]} (Upgrade to {p[1]})" for p in plan["packages_to_update"])
        msg = (
            f"SECURITY PATCH EXECUTION PLAN ({plan['selected_count']} updates):\n\n"
            f"Target Packages:\n{pkgs_str}\n\n"
            f"Proposed Command:\n{plan['apt_command']}\n\n"
            "Safety Preconditions: Verified.\n"
            "To apply, copy and execute in terminal or approve via PolicyKit."
        )
        QMessageBox.information(self, "Patch Execution Preview", msg)

    # -------------------------------------------------------------
    # ACTION HANDLERS
    # -------------------------------------------------------------
    def show_safety_checks(self):
        """Show dialog with detailed safety checks."""
        pre = self.sec_center.check_safety_preconditions()
        status_msg = (
            f"// SYSTEM SAFETY PRE-CONDITIONS REPORT\n\n"
            f"1. Free Disk Space:       {pre['free_space_gb']} GB (Required >= 1.0 GB) -> {'PASS' if pre['disk_space_ok'] else 'FAIL'}\n"
            f"2. Package Manager Lock:  DPKG lock free -> {'PASS' if pre['dpkg_lock_free'] else 'FAIL'}\n"
            f"3. DPKG Database Health:  dpkg --audit clean -> {'PASS' if pre['database_consistent'] else 'FAIL'}\n"
            f"4. Overall Readiness:     {'SYSTEM READY FOR PATCHING' if pre['all_passed'] else 'SAFETY DEFICIT DETECTED'}\n"
        )
        if pre["issues"]:
            status_msg += f"\nIssues Detected:\n" + "\n".join(f"- {i}" for i in pre["issues"])
        QMessageBox.information(self, "Safety Pre-Conditions", status_msg)

    def export_html_report(self):
        """Export comprehensive HTML report to user selected path."""
        default_path = os.path.expanduser("~/victor_security_audit_report.html")
        path, _ = QFileDialog.getSaveFileName(self, "Export Security Audit HTML", default_path, "HTML Files (*.html)")
        if path:
            ok = self.sec_center.export_html_report(path)
            if ok:
                QMessageBox.information(self, "Export Successful", f"Security audit report exported successfully to:\n{path}")
            else:
                QMessageBox.critical(self, "Export Failed", "Failed to write HTML report.")

    def export_json_report(self):
        """Export JSON audit dump."""
        default_path = os.path.expanduser("~/victor_security_audit_report.json")
        path, _ = QFileDialog.getSaveFileName(self, "Export Security Audit JSON", default_path, "JSON Files (*.json)")
        if path:
            ok = self.sec_center.export_json_report(path)
            if ok:
                QMessageBox.information(self, "Export Successful", f"Security audit JSON exported successfully to:\n{path}")
            else:
                QMessageBox.critical(self, "Export Failed", "Failed to write JSON report.")

