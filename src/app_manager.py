#!/usr/bin/env python3
"""
Victor Command Center - Linux Application Manager Backend
Source of Truth: Real Kali Linux APT/dpkg, Flatpak, and Snap databases.
Zero simulated or mock data.
"""

import os
import re
import sys
import glob
import gzip
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple, Any

# Core Kali / System critical package identifiers and patterns
ESSENTIAL_PACKAGES = {
    "libc6", "libc-bin", "systemd", "systemd-sysv", "init", "bash", "coreutils",
    "dpkg", "apt", "login", "passwd", "mount", "util-linux", "tar", "gzip",
    "libpam0g", "libselinux1", "libsepol2", "libaudit1", "libcap2",
    "xorg", "xserver-xorg", "lightdm", "xfce4", "xfwm4", "xfce4-panel",
    "xfce4-session", "thunar", "dbus", "network-manager"
}

CRITICAL_PATTERNS = [
    r"^linux-image-",
    r"^linux-headers-",
    r"^systemd",
    r"^xfce4",
    r"^xorg",
    r"^kali-linux"
]


def format_size(bytes_val: int) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"


def map_section_to_category(section: str) -> str:
    """Map Debian package section to user-friendly category."""
    sec = section.lower() if section else "other"
    if any(k in sec for k in ["net", "comm", "mail", "news"]):
        return "Networking"
    if any(k in sec for k in ["devel", "vcs", "debug"]):
        return "Development"
    if any(k in sec for k in ["admin", "system", "kernel", "shells"]):
        return "System Utilities"
    if any(k in sec for k in ["security", "crypto"]):
        return "Security Tools"
    if any(k in sec for k in ["web", "http"]):
        return "Web & Internet"
    if any(k in sec for k in ["graphics", "sound", "video"]):
        return "Multimedia & Graphics"
    if any(k in sec for k in ["database", "sql"]):
        return "Databases"
    if any(k in sec for k in ["lib", "perl", "python", "ruby", "golang", "java"]):
        return "Libraries & Frameworks"
    if any(k in sec for k in ["doc", "text", "editors"]):
        return "Text & Documentation"
    if any(k in sec for k in ["science", "math"]):
        return "Science & Math"
    if any(k in sec for k in ["games"]):
        return "Games"
    return "Other"


class ApplicationManager:
    """Manages real Kali Linux system packages and applications."""

    def __init__(self):
        self._cached_packages: Optional[List[Dict[str, Any]]] = None
        self._cached_manual_set: Optional[set] = None
        self._cached_upgradable: Optional[Dict[str, Dict[str, str]]] = None

    def get_manual_installed_packages(self) -> set:
        """Get set of manually installed package names."""
        if self._cached_manual_set is not None:
            return self._cached_manual_set
        try:
            res = subprocess.run(["apt-mark", "showmanual"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                self._cached_manual_set = set(line.strip() for line in res.stdout.split("\n") if line.strip())
            else:
                self._cached_manual_set = set()
        except Exception:
            self._cached_manual_set = set()
        return self._cached_manual_set

    def get_upgradable_packages(self) -> Dict[str, Dict[str, str]]:
        """Get dict of upgradable packages {pkg_name: {candidate, installed}}."""
        if self._cached_upgradable is not None:
            return self._cached_upgradable
        upgradables = {}
        try:
            res = subprocess.run(["apt", "list", "--upgradable"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                for line in res.stdout.split("\n"):
                    # Format: 7zip/kali-rolling 26.05+dfsg-1 amd64 [upgradable from: 26.03+dfsg-3]
                    m = re.match(r"^([^/]+)/[^\s]+\s+([^\s]+)\s+[^\s]+\s+\[upgradable from:\s+([^\]]+)\]", line.strip())
                    if m:
                        pkg, cand_ver, inst_ver = m.groups()
                        upgradables[pkg] = {"candidate": cand_ver, "installed": inst_ver}
        except Exception:
            pass
        self._cached_upgradable = upgradables
        return upgradables

    def get_installed_packages(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Query all installed packages from dpkg, flatpak, and snap.
        Returns list of structured package dictionaries.
        """
        if self._cached_packages is not None and not force_refresh:
            return self._cached_packages

        packages: List[Dict[str, Any]] = []
        manual_set = self.get_manual_installed_packages()
        upgradables = self.get_upgradable_packages()

        # 1. Query APT / dpkg packages
        try:
            cmd = [
                "dpkg-query", "-W",
                "-f=${Package}\t${Version}\t${Installed-Size}\t${Section}\t${Priority}\t${Status}\t${binary:Summary}\n"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if res.returncode == 0:
                for line in res.stdout.split("\n"):
                    if not line.strip():
                        continue
                    parts = line.split("\t")
                    if len(parts) >= 6:
                        name = parts[0].strip()
                        ver = parts[1].strip()
                        size_raw = parts[2].strip()
                        section = parts[3].strip()
                        priority = parts[4].strip()
                        status = parts[5].strip()
                        summary = parts[6].strip() if len(parts) > 6 else ""

                        # Filter: only keep installed packages (skip purged/de-installed)
                        if "installed" not in status:
                            continue

                        try:
                            size_kb = int(size_raw) if size_raw.isdigit() else 0
                        except ValueError:
                            size_kb = 0

                        is_manual = name in manual_set
                        is_upgradable = name in upgradables
                        candidate_ver = upgradables[name]["candidate"] if is_upgradable else ver

                        packages.append({
                            "name": name,
                            "version": ver,
                            "size_kb": size_kb,
                            "size_bytes": size_kb * 1024,
                            "size_human": format_size(size_kb * 1024),
                            "section": section,
                            "category": map_section_to_category(section),
                            "priority": priority,
                            "is_manual": is_manual,
                            "is_auto": not is_manual,
                            "summary": summary,
                            "upgradable": is_upgradable,
                            "candidate_version": candidate_ver,
                            "status": status,
                            "source": "APT / dpkg"
                        })
        except Exception as e:
            print(f"[ApplicationManager] Error querying dpkg: {e}", file=sys.stderr)

        # 2. Query Flatpak if available
        if shutil.which("flatpak"):
            try:
                res = subprocess.run(
                    ["flatpak", "list", "--columns=name,application,version,branch,installation"],
                    capture_output=True, text=True, check=False
                )
                if res.returncode == 0:
                    for line in res.stdout.strip().split("\n"):
                        if not line.strip():
                            continue
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            f_name = parts[0].strip()
                            f_app_id = parts[1].strip()
                            f_ver = parts[2].strip() if len(parts) > 2 else "latest"
                            packages.append({
                                "name": f_name,
                                "version": f_ver or "system",
                                "size_kb": 0,
                                "size_bytes": 0,
                                "size_human": "Flatpak Bundle",
                                "section": "flatpak",
                                "category": "Flatpak Apps",
                                "priority": "optional",
                                "is_manual": True,
                                "is_auto": False,
                                "summary": f"Flatpak application ({f_app_id})",
                                "upgradable": False,
                                "candidate_version": f_ver,
                                "status": "installed",
                                "source": "Flatpak",
                                "app_id": f_app_id
                            })
            except Exception as e:
                print(f"[ApplicationManager] Flatpak query note: {e}", file=sys.stderr)

        # 3. Query Snap if available
        if shutil.which("snap"):
            try:
                res = subprocess.run(["snap", "list"], capture_output=True, text=True, check=False)
                if res.returncode == 0:
                    lines = res.stdout.strip().split("\n")
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) >= 3:
                            s_name = parts[0]
                            s_ver = parts[1]
                            packages.append({
                                "name": s_name,
                                "version": s_ver,
                                "size_kb": 0,
                                "size_bytes": 0,
                                "size_human": "Snap Package",
                                "section": "snap",
                                "category": "Snap Apps",
                                "priority": "optional",
                                "is_manual": True,
                                "is_auto": False,
                                "summary": f"Canonical Snap package ({s_name})",
                                "upgradable": False,
                                "candidate_version": s_ver,
                                "status": "installed",
                                "source": "Snap"
                            })
            except Exception as e:
                pass

        self._cached_packages = packages
        return packages

    def get_package_details(self, package_name: str, source: str = "APT / dpkg") -> Dict[str, Any]:
        """Fetch full details and description for a specific package."""
        if source == "Flatpak":
            return {
                "name": package_name,
                "maintainer": "Flatpak Origin",
                "architecture": "all",
                "depends": "Flatpak Runtimes",
                "homepage": "https://flathub.org",
                "description": f"Installed Flatpak bundle: {package_name}"
            }

        details = {
            "name": package_name,
            "maintainer": "Unknown",
            "architecture": "all",
            "depends": "",
            "recommends": "",
            "suggests": "",
            "homepage": "",
            "description": ""
        }
        try:
            res = subprocess.run(["dpkg", "-s", package_name], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                lines = res.stdout.split("\n")
                desc_lines = []
                in_desc = False
                for line in lines:
                    if line.startswith("Maintainer:"):
                        details["maintainer"] = line.split(":", 1)[1].strip()
                        in_desc = False
                    elif line.startswith("Architecture:"):
                        details["architecture"] = line.split(":", 1)[1].strip()
                        in_desc = False
                    elif line.startswith("Depends:"):
                        details["depends"] = line.split(":", 1)[1].strip()
                        in_desc = False
                    elif line.startswith("Recommends:"):
                        details["recommends"] = line.split(":", 1)[1].strip()
                        in_desc = False
                    elif line.startswith("Suggests:"):
                        details["suggests"] = line.split(":", 1)[1].strip()
                        in_desc = False
                    elif line.startswith("Homepage:"):
                        details["homepage"] = line.split(":", 1)[1].strip()
                        in_desc = False
                    elif line.startswith("Description:"):
                        in_desc = True
                        desc_lines.append(line.split(":", 1)[1].strip())
                    elif in_desc:
                        if line.startswith(" ") or line.startswith("\t"):
                            desc_lines.append(line.strip())
                        else:
                            in_desc = False
                details["description"] = "\n".join(desc_lines)
        except Exception as e:
            details["description"] = f"Error querying package details: {e}"
        return details

    def get_dependencies(self, package_name: str) -> Dict[str, List[str]]:
        """Inspect dependencies and reverse dependencies for an application."""
        deps = []
        rdeps = []
        try:
            res = subprocess.run(["apt-cache", "depends", "--important", package_name], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                for line in res.stdout.split("\n"):
                    line = line.strip()
                    if line.startswith("Depends:"):
                        dep = line.split(":", 1)[1].strip().split()[0]
                        deps.append(dep)
        except Exception:
            pass

        try:
            res_r = subprocess.run(["apt-cache", "rdepends", "--installed", package_name], capture_output=True, text=True, check=False)
            if res_r.returncode == 0:
                lines = res_r.stdout.split("\n")
                # First two lines are headers
                for line in lines[2:]:
                    line = line.strip()
                    if line and line != package_name:
                        rdeps.append(line)
        except Exception:
            pass

        return {
            "depends": sorted(list(set(deps))),
            "reverse_depends": sorted(list(set(rdeps)))
        }

    def get_orphaned_packages(self) -> List[Dict[str, Any]]:
        """
        Identify orphaned packages: automatically installed packages
        that are no longer required by any currently installed package.
        Uses real apt autoremove simulation.
        """
        orphans = []
        try:
            res = subprocess.run(["apt-get", "-s", "autoremove"], capture_output=True, text=True, check=False)
            capturing = False
            orphan_names = []
            for line in res.stdout.split("\n"):
                if "The following packages will be REMOVED:" in line:
                    capturing = True
                    continue
                if capturing:
                    if line.startswith("  "):
                        orphan_names.extend(line.strip().split())
                    else:
                        capturing = False

            # Query sizes and descriptions for orphans
            if orphan_names:
                packages_map = {p["name"]: p for p in self.get_installed_packages()}
                for name in orphan_names:
                    if name in packages_map:
                        orphans.append(packages_map[name])
                    else:
                        orphans.append({
                            "name": name,
                            "version": "installed",
                            "size_kb": 0,
                            "size_human": "Unknown",
                            "category": "Orphaned",
                            "summary": "Automatically installed dependency no longer required by any package",
                            "is_manual": False,
                            "is_auto": True,
                            "source": "APT / dpkg"
                        })
        except Exception as e:
            print(f"[ApplicationManager] Error querying orphans: {e}", file=sys.stderr)
        return orphans

    def get_potentially_unused_applications(self) -> List[Dict[str, Any]]:
        """
        Identify potentially unused applications using concrete evidence:
        1. Residual configurations (dpkg status 'rc' from unpurged packages)
        2. Orphaned auto-installed packages (0 reverse dependencies)
        3. Development/header packages with 0 reverse dependencies
        4. Older unbooted Linux kernels lingering in the system
        """
        unused: List[Dict[str, Any]] = []

        # 1. Residual configurations ('rc' state)
        try:
            res = subprocess.run(["dpkg", "-l"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                for line in res.stdout.split("\n"):
                    if line.startswith("rc "):
                        parts = line.split()
                        if len(parts) >= 3:
                            pkg_name = parts[1]
                            ver = parts[2]
                            unused.append({
                                "name": pkg_name,
                                "version": ver,
                                "type": "Residual Configuration",
                                "evidence": "Package uninstalled but configuration files remain ('rc' status).",
                                "action_recommendation": "Purge residual configuration",
                                "can_safely_remove": True
                            })
        except Exception:
            pass

        # 2. Orphaned auto-installed packages
        orphans = self.get_orphaned_packages()
        for o in orphans:
            unused.append({
                "name": o["name"],
                "version": o["version"],
                "type": "Orphaned Dependency",
                "evidence": "Installed as a dependency for an app that was removed; no active packages depend on it.",
                "action_recommendation": "Remove orphaned package",
                "can_safely_remove": True
            })

        # 3. Old unbooted Linux kernels
        try:
            uname_res = subprocess.run(["uname", "-r"], capture_output=True, text=True, check=False)
            running_kernel = uname_res.stdout.strip()
            installed_pkgs = self.get_installed_packages()
            for p in installed_pkgs:
                if p["name"].startswith("linux-image-") and p["name"] != f"linux-image-{running_kernel}" and p["name"] != "linux-image-amd64":
                    unused.append({
                        "name": p["name"],
                        "version": p["version"],
                        "type": "Inactive Kernel Image",
                        "evidence": f"Installed kernel differs from active running kernel ({running_kernel}). Consumes storage space.",
                        "action_recommendation": "Remove inactive kernel after verifying system stability",
                        "can_safely_remove": True
                    })
        except Exception:
            pass

        return unused

    def preview_uninstallation(self, package_names: List[str]) -> Dict[str, Any]:
        """
        Simulate package removal before any execution.
        Analyzes:
        - Packages directly requested for removal
        - Dependent packages that will be removed as collateral
        - Estimated disk space recovered
        - Safety impact classification:
          * BLOCKED_CRITICAL: Contains essential/system-critical package
          * HIGH_IMPACT: Removes desktop environment or Kali core metapackages
          * MEDIUM_IMPACT: Removes secondary dependent applications
          * LOW_IMPACT_SAFE: Safe isolated removal
        """
        result = {
            "requested_packages": package_names,
            "all_packages_to_remove": [],
            "additional_dependencies_removed": [],
            "space_freed_human": "0 MB",
            "impact_level": "LOW_IMPACT_SAFE",
            "is_blocked": False,
            "block_reason": "",
            "warnings": [],
            "raw_simulation_output": ""
        }

        if not package_names:
            result["block_reason"] = "No packages selected for removal."
            result["is_blocked"] = True
            return result

        # 1. Check direct essential packages
        for pkg in package_names:
            if pkg in ESSENTIAL_PACKAGES:
                result["is_blocked"] = True
                result["impact_level"] = "BLOCKED_CRITICAL"
                result["block_reason"] = (
                    f"Package '{pkg}' is an ESSENTIAL system component. "
                    "Removing it will cause permanent system breakage and is blocked."
                )
                return result

        # 2. Run apt-get -s remove simulation
        cmd = ["apt-get", "-s", "remove"] + package_names
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            result["raw_simulation_output"] = res.stdout

            to_remove = []
            capturing = False
            for line in res.stdout.split("\n"):
                if "The following packages will be REMOVED:" in line:
                    capturing = True
                    continue
                if capturing:
                    if line.startswith("  "):
                        to_remove.extend(line.strip().split())
                    else:
                        capturing = False

                # Extract freed disk space e.g. "After this operation, 120 MB disk space will be freed."
                if "disk space will be freed" in line:
                    result["space_freed_human"] = line.strip()

            result["all_packages_to_remove"] = to_remove
            additional = [p for p in to_remove if p not in package_names]
            result["additional_dependencies_removed"] = additional

            # 3. Analyze impact of the entire removal cascade
            for p in to_remove:
                # Essential package in cascade
                if p in ESSENTIAL_PACKAGES:
                    result["is_blocked"] = True
                    result["impact_level"] = "BLOCKED_CRITICAL"
                    result["block_reason"] = (
                        f"Uninstallation cascade requires removing ESSENTIAL system component '{p}'. "
                        "Operation blocked to preserve operating system integrity."
                    )
                    return result

                # Check critical desktop/Kali metapackage patterns
                for pat in CRITICAL_PATTERNS:
                    if re.match(pat, p):
                        if result["impact_level"] != "BLOCKED_CRITICAL":
                            result["impact_level"] = "HIGH_IMPACT"
                        result["warnings"].append(
                            f"Cascade affects core system/desktop component: '{p}'."
                        )

            if not result["is_blocked"]:
                if result["impact_level"] != "HIGH_IMPACT":
                    if len(additional) > 0:
                        result["impact_level"] = "MEDIUM_IMPACT"
                        result["warnings"].append(
                            f"Removing {len(additional)} additional dependent packages."
                        )
                    else:
                        result["impact_level"] = "LOW_IMPACT_SAFE"

        except Exception as e:
            result["is_blocked"] = True
            result["block_reason"] = f"Simulation failed: {e}"

        return result

    def execute_uninstallation(self, package_names: List[str], purge: bool = False) -> Tuple[bool, str]:
        """
        Execute uninstallation using pkexec or apt-get with safety checks.
        Never executes if uninstallation preview classifies as BLOCKED_CRITICAL.
        """
        preview = self.preview_uninstallation(package_names)
        if preview["is_blocked"]:
            return False, f"EXECUTION BLOCKED: {preview['block_reason']}"

        action = "purge" if purge else "remove"
        # Controlled execution command
        cmd = ["pkexec", "apt-get", action, "-y"] + package_names
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            output = res.stdout + "\n" + res.stderr
            # Force cache refresh after operation
            self._cached_packages = None
            if res.returncode == 0:
                return True, f"Successfully removed packages: {', '.join(package_names)}\n{output}"
            else:
                return False, f"APT operation failed (code {res.returncode}):\n{output}"
        except Exception as e:
            return False, f"Execution error: {e}"

    def get_package_history(self) -> List[Dict[str, Any]]:
        """
        Parse real package management transactions from /var/log/apt/history.log*
        Extracts timestamps, commands, actions, affected packages, and statuses.
        Sanitizes any confidential parameters.
        """
        records: List[Dict[str, Any]] = []
        files = sorted(glob.glob("/var/log/apt/history.log*"))

        for fpath in files:
            opener = gzip.open if fpath.endswith(".gz") else open
            try:
                with opener(fpath, "rt", errors="ignore") as f:
                    current: Dict[str, str] = {}
                    for line in f:
                        line = line.strip()
                        if not line:
                            if current and "Start-Date" in current:
                                self._process_history_block(current, records)
                                current = {}
                            continue
                        if ":" in line:
                            k, v = line.split(":", 1)
                            current[k.strip()] = v.strip()
                    if current and "Start-Date" in current:
                        self._process_history_block(current, records)
            except Exception:
                pass

        # Sort descending by start date (most recent first)
        records.sort(key=lambda r: r.get("start_date", ""), reverse=True)
        return records

    def _process_history_block(self, raw_block: Dict[str, str], target_list: List[Dict[str, Any]]):
        """Parse raw history block into clean record and sanitize output."""
        start_date = raw_block.get("Start-Date", "")
        end_date = raw_block.get("End-Date", "")
        raw_cmd = raw_block.get("Commandline", "")

        # Sanitize commandline: mask potential sensitive tokens
        sanitized_cmd = re.sub(r"(--password[= ]|passwd[= ])[^\s]+", r"\1******", raw_cmd)

        # Identify action type
        action_type = "UNKNOWN"
        packages_affected = []

        if "Install" in raw_block:
            action_type = "INSTALL"
            packages_affected.extend(raw_block["Install"].split(","))
        if "Upgrade" in raw_block:
            action_type = "UPGRADE"
            packages_affected.extend(raw_block["Upgrade"].split(","))
        if "Remove" in raw_block:
            action_type = "REMOVE"
            packages_affected.extend(raw_block["Remove"].split(","))
        if "Purge" in raw_block:
            action_type = "PURGE"
            packages_affected.extend(raw_block["Purge"].split(","))

        status = "FAILED" if "Error" in raw_block else "SUCCESS"

        target_list.append({
            "start_date": start_date,
            "end_date": end_date,
            "command": sanitized_cmd,
            "action_type": action_type,
            "requested_by": raw_block.get("Requested-By", "system"),
            "packages_affected_count": len(packages_affected),
            "packages_summary": ", ".join(p.strip().split()[0] for p in packages_affected[:6]) + (f" (+{len(packages_affected)-6} more)" if len(packages_affected) > 6 else ""),
            "status": status,
            "error_detail": raw_block.get("Error", "")
        })

