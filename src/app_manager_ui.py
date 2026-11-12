#!/usr/bin/env python3
"""
Victor Command Center - Linux Application Manager UI
PyQt6 Interface for real Kali Linux APT/dpkg, Flatpak, and Snap management.
"""

import sys
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QTabWidget, QTextEdit, QMessageBox, QGroupBox, QSplitter, QCheckBox,
    QProgressBar, QFrame
)

from app_manager import ApplicationManager, ESSENTIAL_PACKAGES


class NumericTableWidgetItem(QTableWidgetItem):
    """Table item that sorts numerically by a given value."""
    def __init__(self, display_text: str, sort_value: float):
        super().__init__(display_text)
        self.sort_value = sort_value

    def __lt__(self, other):
        if isinstance(other, NumericTableWidgetItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)


class PackageDetailsDialog(QDialog):
    """Inspect full package metadata, dependencies, and descriptions."""

    def __init__(self, package_info: Dict[str, Any], app_mgr: ApplicationManager, parent=None):
        super().__init__(parent)
        self.pkg = package_info
        self.app_mgr = app_mgr
        self.setWindowTitle(f"Package Inspector // {self.pkg['name']}")
        self.resize(750, 560)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header Banner
        header = QFrame()
        header.setStyleSheet("background: #111820; border: 1px solid #1F2E3D; border-radius: 4px; padding: 10px;")
        h_layout = QVBoxLayout(header)
        lbl_name = QLabel(f"// PACKAGE: {self.pkg['name']} ({self.pkg['version']})")
        lbl_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #39FF88; font-family: monospace;")
        lbl_sub = QLabel(f"Source: {self.pkg['source']}  |  Category: {self.pkg['category']}  |  Installed Size: {self.pkg['size_human']}")
        lbl_sub.setStyleSheet("font-size: 12px; color: #00D9FF; font-family: monospace;")
        h_layout.addWidget(lbl_name)
        h_layout.addWidget(lbl_sub)
        layout.addWidget(header)

        # Details Tabs
        tabs = QTabWidget()

        # Tab 1: Overview & Description
        w_overview = QWidget()
        v_over = QVBoxLayout(w_overview)
        details = self.app_mgr.get_package_details(self.pkg["name"], self.pkg.get("source", "APT / dpkg"))

        meta_text = (
            f"Package Name: {details['name']}\n"
            f"Version:      {self.pkg['version']}\n"
            f"Architecture: {details['architecture']}\n"
            f"Maintainer:   {details['maintainer']}\n"
            f"Homepage:     {details['homepage'] or 'N/A'}\n"
            f"Install Type: {'Manual' if self.pkg.get('is_manual') else 'Automatic Dependency'}\n"
            f"Priority:     {self.pkg.get('priority', 'optional')}\n"
        )
        txt_meta = QTextEdit()
        txt_meta.setReadOnly(True)
        txt_meta.setText(meta_text)
        txt_meta.setStyleSheet("background: #080C0B; color: #00D9FF; font-family: monospace; border: 1px solid #1F2E3D;")
        txt_meta.setMaximumHeight(140)
        v_over.addWidget(txt_meta)

        lbl_desc_title = QLabel("Package Description:")
        lbl_desc_title.setStyleSheet("font-weight: bold; color: #39FF88; font-family: monospace;")
        v_over.addWidget(lbl_desc_title)

        txt_desc = QTextEdit()
        txt_desc.setReadOnly(True)
        txt_desc.setText(details["description"] or self.pkg.get("summary", "No description available."))
        txt_desc.setStyleSheet("background: #080C0B; color: #D6E5DF; font-family: monospace; border: 1px solid #1F2E3D;")
        v_over.addWidget(txt_desc)
        tabs.addTab(w_overview, "OVERVIEW & DESCRIPTION")

        # Tab 2: Dependencies
        w_deps = QWidget()
        v_deps = QVBoxLayout(w_deps)
        dep_data = self.app_mgr.get_dependencies(self.pkg["name"])

        v_deps.addWidget(QLabel("Direct Package Dependencies (Requires to function):"))
        txt_deps = QTextEdit()
        txt_deps.setReadOnly(True)
        txt_deps.setText("\n".join(dep_data["depends"]) if dep_data["depends"] else "None (Standalone package)")
        txt_deps.setStyleSheet("background: #080C0B; color: #39FF88; font-family: monospace; border: 1px solid #1F2E3D;")
        v_deps.addWidget(txt_deps)

        v_deps.addWidget(QLabel("Reverse Dependencies (Installed applications depending on this):"))
        txt_rdeps = QTextEdit()
        txt_rdeps.setReadOnly(True)
        txt_rdeps.setText("\n".join(dep_data["reverse_depends"]) if dep_data["reverse_depends"] else "None (No installed packages depend on this)")
        txt_rdeps.setStyleSheet("background: #080C0B; color: #FFD700; font-family: monospace; border: 1px solid #1F2E3D;")
        v_deps.addWidget(txt_rdeps)

        tabs.addTab(w_deps, "DEPENDENCIES & REVERSE DEPS")

        layout.addWidget(tabs)

        # Close button
        btn_close = QPushButton("CLOSE")
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("background: #111820; color: #39FF88; border: 1px solid #39FF88; padding: 8px; font-weight: bold;")
        layout.addWidget(btn_close)


class SafeUninstallDialog(QDialog):
    """
    Defensive Uninstallation Dialog.
    Previews full dependency cascade, space recovered, and blocks removal of essential components.
    """

    def __init__(self, package_names: List[str], app_mgr: ApplicationManager, parent=None):
        super().__init__(parent)
        self.package_names = package_names
        self.app_mgr = app_mgr
        self.preview = self.app_mgr.preview_uninstallation(package_names)
        self.setWindowTitle("Safe Application Uninstallation // Victor Command Center")
        self.resize(720, 580)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Header
        lbl_h = QLabel("// UNINSTALLATION SAFETY PREVIEW & IMPACT ASSESSMENT")
        lbl_h.setStyleSheet("font-size: 15px; font-weight: bold; color: #39FF88; font-family: monospace;")
        layout.addWidget(lbl_h)

        # Impact Classification Banner
        banner = QFrame()
        b_layout = QVBoxLayout(banner)
        impact = self.preview["impact_level"]

        if self.preview["is_blocked"]:
            banner.setStyleSheet("background: #330A12; border: 2px solid #FF3366; border-radius: 4px; padding: 12px;")
            lbl_status = QLabel("CRITICAL: REMOVAL OPERATION BLOCKED")
            lbl_status.setStyleSheet("color: #FF3366; font-weight: bold; font-size: 14px; font-family: monospace;")
            lbl_msg = QLabel(self.preview["block_reason"])
            lbl_msg.setWordWrap(True)
            lbl_msg.setStyleSheet("color: #D6E5DF;")
            b_layout.addWidget(lbl_status)
            b_layout.addWidget(lbl_msg)
        elif impact == "HIGH_IMPACT":
            banner.setStyleSheet("background: #331A05; border: 2px solid #FF8800; border-radius: 4px; padding: 12px;")
            lbl_status = QLabel("WARNING: HIGH IMPACT ON KALI / DESKTOP COMPONENTS")
            lbl_status.setStyleSheet("color: #FF8800; font-weight: bold; font-size: 14px; font-family: monospace;")
            lbl_msg = QLabel(
                "This removal will also remove core desktop or Kali metapackages! "
                "Explicit manual confirmation is strictly required to proceed."
            )
            lbl_msg.setWordWrap(True)
            lbl_msg.setStyleSheet("color: #D6E5DF;")
            b_layout.addWidget(lbl_status)
            b_layout.addWidget(lbl_msg)
        elif impact == "MEDIUM_IMPACT":
            banner.setStyleSheet("background: #2B2A05; border: 1px solid #FFD700; border-radius: 4px; padding: 12px;")
            lbl_status = QLabel("NOTICE: SECONDARY DEPENDENCIES WILL BE REMOVED")
            lbl_status.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 13px; font-family: monospace;")
            lbl_msg = QLabel("Additional dependent packages will be uninstalled along with the selected package.")
            lbl_msg.setStyleSheet("color: #D6E5DF;")
            b_layout.addWidget(lbl_status)
            b_layout.addWidget(lbl_msg)
        else:
            banner.setStyleSheet("background: #0A2216; border: 1px solid #39FF88; border-radius: 4px; padding: 12px;")
            lbl_status = QLabel("SAFE: ISOLATED APPLICATION REMOVAL")
            lbl_status.setStyleSheet("color: #39FF88; font-weight: bold; font-size: 13px; font-family: monospace;")
            lbl_msg = QLabel("No essential or collateral system applications are negatively impacted.")
            lbl_msg.setStyleSheet("color: #D6E5DF;")
            b_layout.addWidget(lbl_status)
            b_layout.addWidget(lbl_msg)

        layout.addWidget(banner)

        # Removal Cascade Details
        lbl_cascade = QLabel(f"Target Packages ({len(self.package_names)}): {', '.join(self.package_names)}")
        lbl_cascade.setStyleSheet("font-weight: bold; color: #00D9FF; font-family: monospace;")
        layout.addWidget(lbl_cascade)

        lbl_freed = QLabel(f"Storage Space Impact: {self.preview.get('space_freed_human', 'N/A')}")
        lbl_freed.setStyleSheet("color: #39FF88; font-family: monospace; font-size: 13px;")
        layout.addWidget(lbl_freed)

        if self.preview["additional_dependencies_removed"]:
            lbl_add = QLabel(f"Additional Collateral Packages To Be Removed ({len(self.preview['additional_dependencies_removed'])}):")
            lbl_add.setStyleSheet("color: #FF8800; font-weight: bold; font-family: monospace;")
            layout.addWidget(lbl_add)

            txt_add = QTextEdit()
            txt_add.setReadOnly(True)
            txt_add.setText(", ".join(self.preview["additional_dependencies_removed"]))
            txt_add.setStyleSheet("background: #080C0B; color: #FF8800; font-family: monospace; border: 1px solid #1F2E3D;")
            txt_add.setMaximumHeight(100)
            layout.addWidget(txt_add)

        # Confirmation controls
        self.chk_confirm = QCheckBox("I have reviewed the uninstallation impact and confirm package removal.")
        self.chk_confirm.setStyleSheet("color: #D6E5DF; font-size: 13px;")
        self.chk_confirm.stateChanged.connect(self.validate_can_uninstall)
        layout.addWidget(self.chk_confirm)

        self.input_confirm = QLineEdit()
        self.input_confirm.setPlaceholderText("Type 'REMOVE' to confirm high-impact operation...")
        self.input_confirm.setStyleSheet("background: #080C0B; color: #FF3366; border: 1px solid #1F2E3D; padding: 6px; font-family: monospace;")
        self.input_confirm.textChanged.connect(self.validate_can_uninstall)

        if impact == "HIGH_IMPACT":
            layout.addWidget(QLabel("High-Impact Security Safeguard: Type 'REMOVE' below to unlock:"))
            layout.addWidget(self.input_confirm)
        else:
            self.input_confirm.setVisible(False)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("CANCEL")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setStyleSheet("background: #111820; color: #D6E5DF; border: 1px solid #1F2E3D; padding: 8px 18px; font-weight: bold;")
        btn_layout.addWidget(self.btn_cancel)

        self.btn_uninstall = QPushButton("UNINSTALL PACKAGES")
        self.btn_uninstall.setStyleSheet("background: #FF3366; color: #FFFFFF; border: none; padding: 8px 22px; font-weight: bold;")
        self.btn_uninstall.setEnabled(False)
        self.btn_uninstall.clicked.connect(self.execute_removal)
        btn_layout.addWidget(self.btn_uninstall)

        layout.addLayout(btn_layout)

    def validate_can_uninstall(self):
        """Validate whether the user can trigger the uninstallation."""
        if self.preview["is_blocked"]:
            self.btn_uninstall.setEnabled(False)
            return

        is_checked = self.chk_confirm.isChecked()
        if self.preview["impact_level"] == "HIGH_IMPACT":
            text_ok = self.input_confirm.text().strip() == "REMOVE"
            self.btn_uninstall.setEnabled(is_checked and text_ok)
        else:
            self.btn_uninstall.setEnabled(is_checked)

    def execute_removal(self):
        """Execute the actual removal operation via ApplicationManager."""
        self.btn_uninstall.setEnabled(False)
        self.btn_uninstall.setText("UNINSTALLING...")
        success, msg = self.app_mgr.execute_uninstallation(self.package_names)
        if success:
            QMessageBox.information(self, "Uninstallation Complete", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Uninstallation Error", msg)
            self.reject()


class AppManagerTab(QWidget):
    """Main Application Manager Tab Widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.app_mgr = ApplicationManager()
        self.packages_data: List[Dict[str, Any]] = []
        self.init_ui()
        # Initial load
        QTimer.singleShot(100, self.refresh_packages)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Tab Segmenter
        self.subtabs = QTabWidget()
        self.subtabs.setObjectName("subTabs")

        # View 1: Installed Applications
        self.tab_installed = QWidget()
        self.init_installed_view()
        self.subtabs.addTab(self.tab_installed, "INSTALLED APPLICATIONS")

        # View 2: Application Discovery & Health
        self.tab_health = QWidget()
        self.init_health_view()
        self.subtabs.addTab(self.tab_health, "DISCOVERY & CLEANUP")

        # View 3: Package Management History
        self.tab_history = QWidget()
        self.init_history_view()
        self.subtabs.addTab(self.tab_history, "PACKAGE HISTORY")

        layout.addWidget(self.subtabs)

    # -------------------------------------------------------------
    # VIEW 1: INSTALLED APPLICATIONS
    # -------------------------------------------------------------
    def init_installed_view(self):
        layout = QVBoxLayout(self.tab_installed)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Filter bar
        filter_box = QHBoxLayout()
        filter_box.setSpacing(8)

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Search installed applications by name, category, or summary...")
        self.input_search.setStyleSheet("background: #080C0B; color: #39FF88; border: 1px solid #1F2E3D; padding: 7px; font-family: monospace;")
        self.input_search.textChanged.connect(self.apply_filter)
        filter_box.addWidget(self.input_search, stretch=3)

        self.combo_category = QComboBox()
        self.combo_category.addItems([
            "All Categories", "Security Tools", "System Utilities", "Development",
            "Networking", "Web & Internet", "Multimedia & Graphics", "Databases",
            "Libraries & Frameworks", "Flatpak Apps", "Other"
        ])
        self.combo_category.setStyleSheet("background: #111820; color: #D6E5DF; border: 1px solid #1F2E3D; padding: 6px;")
        self.combo_category.currentTextChanged.connect(self.apply_filter)
        filter_box.addWidget(self.combo_category, stretch=1)

        self.combo_source = QComboBox()
        self.combo_source.addItems(["All Sources", "APT / dpkg", "Flatpak", "Snap"])
        self.combo_source.setStyleSheet("background: #111820; color: #D6E5DF; border: 1px solid #1F2E3D; padding: 6px;")
        self.combo_source.currentTextChanged.connect(self.apply_filter)
        filter_box.addWidget(self.combo_source, stretch=1)

        self.combo_sort = QComboBox()
        self.combo_sort.addItems([
            "Sort: Name (A-Z)", "Sort: Name (Z-A)",
            "Sort: Size (Largest)", "Sort: Size (Smallest)",
            "Sort: Upgradable First"
        ])
        self.combo_sort.setStyleSheet("background: #111820; color: #D6E5DF; border: 1px solid #1F2E3D; padding: 6px;")
        self.combo_sort.currentIndexChanged.connect(self.apply_sort)
        filter_box.addWidget(self.combo_sort, stretch=1)

        btn_refresh = QPushButton("REFRESH")
        btn_refresh.setStyleSheet("background: #111820; color: #39FF88; border: 1px solid #39FF88; padding: 6px 14px; font-weight: bold;")
        btn_refresh.clicked.connect(lambda: self.refresh_packages(force=True))
        filter_box.addWidget(btn_refresh)

        layout.addLayout(filter_box)

        # Applications Table
        self.table_apps = QTableWidget(0, 7)
        self.table_apps.setHorizontalHeaderLabels([
            "Package / Application", "Version", "Size", "Category", "Install Type", "Updates", "Source"
        ])
        self.table_apps.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table_apps.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table_apps.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table_apps.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table_apps.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.table_apps.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.table_apps.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        self.table_apps.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_apps.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_apps.setStyleSheet("""
            QTableWidget {
                background-color: #080C0B;
                color: #D6E5DF;
                gridline-color: #1F2E3D;
                font-family: monospace;
            }
            QHeaderView::section {
                background-color: #111820;
                color: #00D9FF;
                padding: 6px;
                border: 1px solid #1F2E3D;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #1A3326;
                color: #39FF88;
            }
        """)
        self.table_apps.itemDoubleClicked.connect(self.inspect_selected_package)
        layout.addWidget(self.table_apps, stretch=1)

        # Action Toolbar
        action_bar = QHBoxLayout()
        self.lbl_table_count = QLabel("Loading packages from real package database...")
        self.lbl_table_count.setStyleSheet("color: #82948C; font-family: monospace; font-size: 12px;")
        action_bar.addWidget(self.lbl_table_count)

        action_bar.addStretch()

        btn_inspect = QPushButton("INSPECT DETAILS")
        btn_inspect.setStyleSheet("background: #111820; color: #00D9FF; border: 1px solid #00D9FF; padding: 7px 16px; font-weight: bold;")
        btn_inspect.clicked.connect(self.inspect_selected_package)
        action_bar.addWidget(btn_inspect)

        btn_uninstall = QPushButton("SAFE UNINSTALL")
        btn_uninstall.setStyleSheet("background: #111820; color: #FF3366; border: 1px solid #FF3366; padding: 7px 16px; font-weight: bold;")
        btn_uninstall.clicked.connect(self.uninstall_selected_package)
        action_bar.addWidget(btn_uninstall)

        layout.addLayout(action_bar)

    def refresh_packages(self, force: bool = False):
        """Fetch real system packages and populate table."""
        self.lbl_table_count.setText("Querying APT/dpkg and Flatpak...")
        self.packages_data = self.app_mgr.get_installed_packages(force_refresh=force)
        self.populate_table(self.packages_data)

    def populate_table(self, packages: List[Dict[str, Any]]):
        """Fill table with package items."""
        self.table_apps.setSortingEnabled(False)
        self.table_apps.setRowCount(0)

        for p in packages:
            row = self.table_apps.rowCount()
            self.table_apps.insertRow(row)

            # Name
            it_name = QTableWidgetItem(p["name"])
            it_name.setData(Qt.ItemDataRole.UserRole, p)
            self.table_apps.setItem(row, 0, it_name)

            # Version
            it_ver = QTableWidgetItem(p["version"])
            self.table_apps.setItem(row, 1, it_ver)

            # Size
            it_size = NumericTableWidgetItem(p["size_human"], p["size_bytes"])
            self.table_apps.setItem(row, 2, it_size)

            # Category
            it_cat = QTableWidgetItem(p["category"])
            self.table_apps.setItem(row, 3, it_cat)

            # Install Type
            type_str = "Manual" if p.get("is_manual") else "Auto Dependency"
            it_type = QTableWidgetItem(type_str)
            if p.get("is_manual"):
                it_type.setForeground(QColor("#39FF88"))
            else:
                it_type.setForeground(QColor("#82948C"))
            self.table_apps.setItem(row, 4, it_type)

            # Updates
            if p.get("upgradable"):
                it_up = QTableWidgetItem(f"Upgradable ({p['candidate_version']})")
                it_up.setForeground(QColor("#00D9FF"))
            else:
                it_up = QTableWidgetItem("Up to date")
                it_up.setForeground(QColor("#82948C"))
            self.table_apps.setItem(row, 5, it_up)

            # Source
            it_src = QTableWidgetItem(p["source"])
            self.table_apps.setItem(row, 6, it_src)

        self.lbl_table_count.setText(f"Showing {len(packages)} installed packages.")
        self.table_apps.setSortingEnabled(True)

    def apply_filter(self):
        """Filter packages table based on search text, category, and source."""
        query = self.input_search.text().strip().lower()
        selected_cat = self.combo_category.currentText()
        selected_src = self.combo_source.currentText()

        filtered = []
        for p in self.packages_data:
            # Query match
            if query:
                match_name = query in p["name"].lower()
                match_desc = query in p.get("summary", "").lower()
                if not (match_name or match_desc):
                    continue

            # Category match
            if selected_cat != "All Categories":
                if p["category"] != selected_cat:
                    continue

            # Source match
            if selected_src != "All Sources":
                if p["source"] != selected_src:
                    continue

            filtered.append(p)

        self.populate_table(filtered)

    def apply_sort(self, index: int):
        """Sort table according to selection."""
        if index == 0:  # Name A-Z
            self.table_apps.sortItems(0, Qt.SortOrder.AscendingOrder)
        elif index == 1:  # Name Z-A
            self.table_apps.sortItems(0, Qt.SortOrder.DescendingOrder)
        elif index == 2:  # Size Largest
            self.table_apps.sortItems(2, Qt.SortOrder.DescendingOrder)
        elif index == 3:  # Size Smallest
            self.table_apps.sortItems(2, Qt.SortOrder.AscendingOrder)
        elif index == 4:  # Upgradable First
            self.table_apps.sortItems(5, Qt.SortOrder.AscendingOrder)

    def get_selected_package(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected package dict."""
        selected_rows = self.table_apps.selectedItems()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        item = self.table_apps.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def inspect_selected_package(self):
        """Open PackageDetailsDialog for selected package."""
        pkg = self.get_selected_package()
        if not pkg:
            QMessageBox.warning(self, "No Selection", "Please select a package from the table to inspect.")
            return
        dlg = PackageDetailsDialog(pkg, self.app_mgr, self)
        dlg.exec()

    def uninstall_selected_package(self):
        """Open SafeUninstallDialog for selected package."""
        pkg = self.get_selected_package()
        if not pkg:
            QMessageBox.warning(self, "No Selection", "Please select a package from the table to uninstall.")
            return

        dlg = SafeUninstallDialog([pkg["name"]], self.app_mgr, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh_packages(force=True)

    # -------------------------------------------------------------
    # VIEW 2: APPLICATION DISCOVERY & HEALTH
    # -------------------------------------------------------------
    def init_health_view(self):
        layout = QVBoxLayout(self.tab_health)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # 1. Orphaned Packages Box
        box_orphans = QGroupBox("ORPHANED DEPENDENCIES (AUTOMATICALLY INSTALLED, NO LONGER REQUIRED)")
        box_orphans.setStyleSheet("QGroupBox { color: #00D9FF; font-weight: bold; border: 1px solid #1F2E3D; margin-top: 6px; padding-top: 10px; font-family: monospace; }")
        v_orph = QVBoxLayout(box_orphans)

        self.table_orphans = QTableWidget(0, 4)
        self.table_orphans.setHorizontalHeaderLabels(["Package Name", "Version", "Size", "Action"])
        self.table_orphans.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_orphans.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_orphans.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_orphans.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_orphans.setStyleSheet("background-color: #080C0B; color: #D6E5DF; font-family: monospace;")
        v_orph.addWidget(self.table_orphans)

        h_orph_btns = QHBoxLayout()
        self.lbl_orph_count = QLabel("Scanning for orphans...")
        self.lbl_orph_count.setStyleSheet("color: #82948C; font-family: monospace;")
        h_orph_btns.addWidget(self.lbl_orph_count)
        h_orph_btns.addStretch()

        btn_clean_all = QPushButton("CLEAN ALL SAFE ORPHANS")
        btn_clean_all.setStyleSheet("background: #111820; color: #39FF88; border: 1px solid #39FF88; padding: 6px 14px; font-weight: bold;")
        btn_clean_all.clicked.connect(self.clean_all_orphans)
        h_orph_btns.addWidget(btn_clean_all)

        v_orph.addLayout(h_orph_btns)
        splitter.addWidget(box_orphans)

        # 2. Potentially Unused Applications Box
        box_unused = QGroupBox("POTENTIALLY UNUSED APPLICATIONS & SYSTEM DRIFT (EVIDENCE-BASED)")
        box_unused.setStyleSheet("QGroupBox { color: #FF8800; font-weight: bold; border: 1px solid #1F2E3D; margin-top: 6px; padding-top: 10px; font-family: monospace; }")
        v_un = QVBoxLayout(box_unused)

        self.table_unused = QTableWidget(0, 4)
        self.table_unused.setHorizontalHeaderLabels(["Component Name", "Issue / Type", "Evidence Rationale", "Recommendation"])
        self.table_unused.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table_unused.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table_unused.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_unused.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table_unused.setStyleSheet("background-color: #080C0B; color: #D6E5DF; font-family: monospace;")
        v_un.addWidget(self.table_unused)

        h_un_btns = QHBoxLayout()
        self.lbl_un_count = QLabel("Scanning system health...")
        self.lbl_un_count.setStyleSheet("color: #82948C; font-family: monospace;")
        h_un_btns.addWidget(self.lbl_un_count)
        h_un_btns.addStretch()

        btn_refresh_health = QPushButton("REFRESH DISCOVERY")
        btn_refresh_health.setStyleSheet("background: #111820; color: #00D9FF; border: 1px solid #00D9FF; padding: 6px 14px; font-weight: bold;")
        btn_refresh_health.clicked.connect(self.refresh_health_data)
        h_un_btns.addWidget(btn_refresh_health)

        v_un.addLayout(h_un_btns)
        splitter.addWidget(box_unused)

        layout.addWidget(splitter)

        # Load initial health data
        QTimer.singleShot(300, self.refresh_health_data)

    def refresh_health_data(self):
        """Fetch and populate orphans and potentially unused items."""
        orphans = self.app_mgr.get_orphaned_packages()
        self.table_orphans.setRowCount(0)
        for o in orphans:
            row = self.table_orphans.rowCount()
            self.table_orphans.insertRow(row)
            self.table_orphans.setItem(row, 0, QTableWidgetItem(o["name"]))
            self.table_orphans.setItem(row, 1, QTableWidgetItem(o["version"]))
            self.table_orphans.setItem(row, 2, QTableWidgetItem(o["size_human"]))

            btn_rem = QPushButton("Remove")
            btn_rem.setStyleSheet("background: #111820; color: #FF3366; border: 1px solid #FF3366; padding: 3px 8px;")
            pkg_name = o["name"]
            btn_rem.clicked.connect(lambda _, n=pkg_name: self.safe_remove_orphan(n))
            self.table_orphans.setCellWidget(row, 3, btn_rem)

        self.lbl_orph_count.setText(f"Found {len(orphans)} orphaned auto-dependencies.")

        # Potentially unused items
        unused = self.app_mgr.get_potentially_unused_applications()
        self.table_unused.setRowCount(0)
        for u in unused:
            row = self.table_unused.rowCount()
            self.table_unused.insertRow(row)
            self.table_unused.setItem(row, 0, QTableWidgetItem(u["name"]))
            self.table_unused.setItem(row, 1, QTableWidgetItem(u["type"]))
            self.table_unused.setItem(row, 2, QTableWidgetItem(u["evidence"]))
            self.table_unused.setItem(row, 3, QTableWidgetItem(u["action_recommendation"]))

        self.lbl_un_count.setText(f"Identified {len(unused)} system health candidates.")

    def safe_remove_orphan(self, pkg_name: str):
        """Launch safe uninstall preview for an orphan."""
        dlg = SafeUninstallDialog([pkg_name], self.app_mgr, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh_health_data()
            self.refresh_packages(force=True)

    def clean_all_orphans(self):
        """Batch remove safe orphans with explicit preview."""
        orphans = self.app_mgr.get_orphaned_packages()
        if not orphans:
            QMessageBox.information(self, "No Orphans", "No orphaned packages found. System is clean.")
            return

        names = [o["name"] for o in orphans]
        dlg = SafeUninstallDialog(names, self.app_mgr, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh_health_data()
            self.refresh_packages(force=True)

    # -------------------------------------------------------------
    # VIEW 3: PACKAGE MANAGEMENT HISTORY
    # -------------------------------------------------------------
    def init_history_view(self):
        layout = QVBoxLayout(self.tab_history)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Filter bar
        f_box = QHBoxLayout()
        self.input_hist_search = QLineEdit()
        self.input_hist_search.setPlaceholderText("Filter transaction history by package or command...")
        self.input_hist_search.setStyleSheet("background: #080C0B; color: #39FF88; border: 1px solid #1F2E3D; padding: 6px; font-family: monospace;")
        self.input_hist_search.textChanged.connect(self.filter_history)
        f_box.addWidget(self.input_hist_search, stretch=3)

        self.combo_hist_action = QComboBox()
        self.combo_hist_action.addItems(["All Actions", "INSTALL", "UPGRADE", "REMOVE", "PURGE"])
        self.combo_hist_action.setStyleSheet("background: #111820; color: #D6E5DF; border: 1px solid #1F2E3D; padding: 6px;")
        self.combo_hist_action.currentTextChanged.connect(self.filter_history)
        f_box.addWidget(self.combo_hist_action, stretch=1)

        btn_hist_refresh = QPushButton("RELOAD LOGS")
        btn_hist_refresh.setStyleSheet("background: #111820; color: #39FF88; border: 1px solid #39FF88; padding: 6px 14px; font-weight: bold;")
        btn_hist_refresh.clicked.connect(self.load_history)
        f_box.addWidget(btn_hist_refresh)

        layout.addLayout(f_box)

        # History Table
        self.table_history = QTableWidget(0, 5)
        self.table_history.setHorizontalHeaderLabels(["Start Date & Time", "Action", "Command Executed", "Affected Packages", "Status"])
        self.table_history.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table_history.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_history.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_history.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table_history.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_history.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_history.setStyleSheet("background-color: #080C0B; color: #D6E5DF; font-family: monospace;")
        self.table_history.itemSelectionChanged.connect(self.display_history_details)
        layout.addWidget(self.table_history, stretch=2)

        # Detail Inspector
        self.txt_hist_details = QTextEdit()
        self.txt_hist_details.setReadOnly(True)
        self.txt_hist_details.setStyleSheet("background: #080C0B; color: #00D9FF; font-family: monospace; border: 1px solid #1F2E3D;")
        self.txt_hist_details.setMaximumHeight(130)
        layout.addWidget(self.txt_hist_details, stretch=1)

        self.history_records: List[Dict[str, Any]] = []
        QTimer.singleShot(400, self.load_history)

    def load_history(self):
        """Load and display package management history."""
        self.history_records = self.app_mgr.get_package_history()
        self.filter_history()

    def filter_history(self):
        """Filter history records based on search and action type."""
        query = self.input_hist_search.text().strip().lower()
        action_filter = self.combo_hist_action.currentText()

        self.table_history.setRowCount(0)
        for r in self.history_records:
            if action_filter != "All Actions" and r["action_type"] != action_filter:
                continue
            if query:
                if query not in r["command"].lower() and query not in r["packages_summary"].lower():
                    continue

            row = self.table_history.rowCount()
            self.table_history.insertRow(row)

            # Date
            it_date = QTableWidgetItem(r["start_date"])
            it_date.setData(Qt.ItemDataRole.UserRole, r)
            self.table_history.setItem(row, 0, it_date)

            # Action
            it_act = QTableWidgetItem(r["action_type"])
            if r["action_type"] == "INSTALL":
                it_act.setForeground(QColor("#39FF88"))
            elif r["action_type"] == "UPGRADE":
                it_act.setForeground(QColor("#00D9FF"))
            elif r["action_type"] in ["REMOVE", "PURGE"]:
                it_act.setForeground(QColor("#FF8800"))
            self.table_history.setItem(row, 1, it_act)

            # Command
            self.table_history.setItem(row, 2, QTableWidgetItem(r["command"]))

            # Affected packages
            self.table_history.setItem(row, 3, QTableWidgetItem(r["packages_summary"]))

            # Status
            it_stat = QTableWidgetItem(r["status"])
            if r["status"] == "SUCCESS":
                it_stat.setForeground(QColor("#39FF88"))
            else:
                it_stat.setForeground(QColor("#FF3366"))
            self.table_history.setItem(row, 4, it_stat)

    def display_history_details(self):
        """Show full sanitized details of selected transaction."""
        selected = self.table_history.selectedItems()
        if not selected:
            self.txt_hist_details.clear()
            return
        row = selected[0].row()
        item = self.table_history.item(row, 0)
        if item:
            r = item.data(Qt.ItemDataRole.UserRole)
            details = (
                f"// TRANSACTION AUDIT RECORD\n"
                f"Start Timestamp: {r['start_date']}\n"
                f"End Timestamp:   {r['end_date']}\n"
                f"Initiated By:    {r['requested_by']}\n"
                f"Action Type:     {r['action_type']} ({r['status']})\n"
                f"Executed Command: {r['command']}\n"
                f"Affected Packages ({r['packages_affected_count']}): {r['packages_summary']}\n"
            )
            if r.get("error_detail"):
                details += f"Error Diagnostics: {r['error_detail']}\n"
            self.txt_hist_details.setText(details)

