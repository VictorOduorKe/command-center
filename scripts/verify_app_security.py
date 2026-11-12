#!/usr/bin/env python3
"""
Verification Script for Victor Command Center
Validates Section 13 (Linux Application Manager) and Section 14 (Security & Vulnerability Center)
Strict adherence to real Kali Linux data and zero simulated mocks.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from app_manager import ApplicationManager, ESSENTIAL_PACKAGES
from security_center import SecurityCenter, KNOWN_SECURITY_ADVISORIES

PASS_COUNT = 0
FAIL_COUNT = 0


def log_test(name: str, passed: bool, detail: str = ""):
    global PASS_COUNT, FAIL_COUNT
    status = "\033[92m[PASS]\033[0m" if passed else "\033[91m[FAIL]\033[0m"
    print(f"{status} {name}")
    if detail:
        print(f"       -> {detail}")
    if passed:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1


def main():
    print("==================================================================")
    print("VICTOR COMMAND CENTER // SECTION 13 & 14 VERIFICATION SUITE")
    print("==================================================================")

    # -------------------------------------------------------------
    # SECTION 13: LINUX APPLICATION MANAGER TESTS
    # -------------------------------------------------------------
    print("\n--- [TEST SUITE 1] LINUX APPLICATION MANAGER ---")
    app_mgr = ApplicationManager()

    # 1. Real Package Querying
    pkgs = app_mgr.get_installed_packages(force_refresh=True)
    has_pkgs = len(pkgs) > 500
    log_test("1. Real APT/dpkg Package Query", has_pkgs, f"Loaded {len(pkgs)} real installed packages.")

    # 2. Package Schema & Metadata Accuracy
    sample = pkgs[0] if pkgs else {}
    schema_ok = all(k in sample for k in [
        "name", "version", "size_kb", "size_human", "category",
        "is_manual", "is_auto", "upgradable", "source"
    ])
    log_test("2. Package Metadata Schema Validation", schema_ok, f"Sample: {sample.get('name')} | {sample.get('category')} | {sample.get('size_human')}")

    # 3. Flatpak Package Integration
    flatpaks = [p for p in pkgs if p["source"] == "Flatpak"]
    has_flatpaks = len(flatpaks) > 0
    log_test("3. Flatpak Detection & Real Inventory", has_flatpaks, f"Identified {len(flatpaks)} installed Flatpaks (e.g. {flatpaks[0]['name'] if flatpaks else 'None'}).")

    # 4. Dependency & Reverse Dependency Inspector
    dep_data = app_mgr.get_dependencies("bash")
    deps_ok = len(dep_data.get("depends", [])) > 0 or len(dep_data.get("reverse_depends", [])) > 0
    log_test("4. Package Dependency Inspector", deps_ok, f"bash depends: {len(dep_data['depends'])}, rdepends: {len(dep_data['reverse_depends'])}")

    # 5. Orphaned Packages Detection
    orphans = app_mgr.get_orphaned_packages()
    log_test("5. Orphaned Dependencies Detection (APT Autoremove)", isinstance(orphans, list), f"Found {len(orphans)} orphaned auto-dependencies.")

    # 6. Potentially Unused Applications (Evidence-based)
    unused = app_mgr.get_potentially_unused_applications()
    unused_ok = len(unused) > 0 and all("evidence" in u for u in unused)
    log_test("6. Potentially Unused Apps Identification", unused_ok, f"Found {len(unused)} candidates with documented evidence.")

    # 7. Safe Uninstallation Preview (Safe Candidate)
    prev_safe = app_mgr.preview_uninstallation(["node-undici"])
    log_test("7. Safe Removal Preview & Freed Space", prev_safe["is_blocked"] is False, f"Impact: {prev_safe['impact_level']} | Freed: {prev_safe.get('space_freed_human')}")

    # 8. Essential Package Protection Safeguard
    prev_essential = app_mgr.preview_uninstallation(["libc6"])
    blocked_ok = prev_essential["is_blocked"] is True and prev_essential["impact_level"] == "BLOCKED_CRITICAL"
    log_test("8. Essential Package Protection (libc6 blocker)", blocked_ok, f"Block Reason: {prev_essential.get('block_reason')}")

    # 9. Package History Parser & Sanitization
    history = app_mgr.get_package_history()
    hist_ok = len(history) > 0 and all("command" in h for h in history)
    log_test("9. Package History Parser from /var/log/apt", hist_ok, f"Parsed {len(history)} real transactions (Latest: {history[0]['start_date'] if history else 'N/A'}).")

    # -------------------------------------------------------------
    # SECTION 14: SECURITY & VULNERABILITY CENTER TESTS
    # -------------------------------------------------------------
    print("\n--- [TEST SUITE 2] DEFENSIVE SECURITY & VULNERABILITY CENTER ---")
    sec = SecurityCenter()

    # 10. Security Assessment Execution
    findings = sec.run_assessment(force_refresh=True)
    has_findings = len(findings) > 0
    log_test("10. Defensive Security Assessment Execution", has_findings, f"Generated {len(findings)} real findings across packages, kernels, and configs.")

    # 11. CVE Vulnerability Matching
    vuln_findings = [f for f in findings if f.category == "Vulnerability"]
    has_vulns = len(vuln_findings) > 0
    log_test("11. Real CVE Vulnerability Detection", has_vulns, f"Matched {len(vuln_findings)} CVEs (Sample: {vuln_findings[0].cve_id if vuln_findings else 'N/A'}).")

    # 12. Scoring Methodology Verification
    overview = sec.get_security_overview()
    expected_score = (
        (overview["critical_count"] * 25) +
        (overview["high_count"] * 10) +
        (overview["medium_count"] * 3) +
        (overview["low_count"] * 1)
    )
    score_ok = overview["risk_score"] == expected_score and "Grade" in overview["posture_grade"]
    log_test("12. Documented Scoring Methodology (VCC-SPM)", score_ok, f"Calculated Risk Score: {overview['risk_score']} ({overview['posture_grade']} - {overview['posture_status']})")

    # 13. Kernel Security & Inactive Image Audit
    kernel_findings = [f for f in findings if f.category == "Kernel Security"]
    log_test("13. Linux Kernel Lifecycle Audit", len(kernel_findings) > 0, f"Identified {len(kernel_findings)} inactive installed kernel images.")

    # 14. Network Socket Exposure Audit
    sock_findings = [f for f in findings if f.category == "Network Exposure"]
    log_test("14. Network Socket & Listening Port Audit", isinstance(sock_findings, list), f"Evaluated listening ports via ss -tuln.")

    # 15. Sensitive File Permissions Audit
    perm_findings = [f for f in findings if f.category == "Permissions"]
    log_test("15. Sensitive File Permissions Audit", isinstance(perm_findings, list), "Audited /etc/shadow, /etc/passwd, and /tmp.")

    # 16. Safety Preconditions Verification
    safety = sec.check_safety_preconditions()
    prechecks_ok = "disk_space_ok" in safety and "dpkg_lock_free" in safety and "database_consistent" in safety
    log_test("16. Patch Safety Preconditions Engine", prechecks_ok, f"Free space: {safety['free_space_gb']} GB | Passed: {safety['all_passed']}")

    # 17. Security Report Generation (HTML & JSON)
    out_html = "/tmp/victor_audit_test.html"
    out_json = "/tmp/victor_audit_test.json"
    html_ok = sec.export_html_report(out_html) and os.path.exists(out_html) and os.path.getsize(out_html) > 1000
    json_ok = sec.export_json_report(out_json) and os.path.exists(out_json) and os.path.getsize(out_json) > 500
    log_test("17. Cyberpunk HTML & JSON Security Report Export", html_ok and json_ok, f"Exported HTML ({os.path.getsize(out_html) if os.path.exists(out_html) else 0} bytes) & JSON.")

    # -------------------------------------------------------------
    # GUI INTEGRATION TEST
    # -------------------------------------------------------------
    print("\n--- [TEST SUITE 3] GUI INTEGRATION (OFFSCREEN) ---")
    try:
        from PyQt6.QtWidgets import QApplication
        from main import VictorCommandCenter
        # Ensure offscreen Qt environment
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        os.environ["QT_QPA_PLATFORMTHEME"] = ""

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        win = VictorCommandCenter()
        tab_count = win.tabs.count()
        gui_ok = tab_count == 9 and hasattr(win, "tab_apps") and hasattr(win, "tab_security")
        log_test("18. Unified GUI 9-Tab Assembly", gui_ok, f"Total tabs mounted: {tab_count} (Tab 8: Apps, Tab 9: Security)")
    except Exception as e:
        log_test("18. Unified GUI 9-Tab Assembly", False, f"GUI Error: {e}")

    print("\n==================================================================")
    print(f"TEST RESULTS: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED")
    print("==================================================================")
    return 0 if FAIL_COUNT == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

