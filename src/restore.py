#!/usr/bin/env python3
"""
Victor Command Center - Restoration & Safety Engine
Restores desktop settings from timestamped backups or baseline Kali configurations.
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

CONFIG_DIR = Path.home() / ".config" / "victor-command-center"
BACKUP_DIR = CONFIG_DIR / "backups"
BASELINE_DIR = BACKUP_DIR / "factory_baseline"
REPO_BASELINE_DIR = Path("/home/alpha/victor-command-center/config/factory_baseline")

# Target system paths
XFCE_PERCHANNEL_DIR = Path.home() / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml"
QTERMINAL_CONFIG = Path.home() / ".config" / "qterminal.org" / "qterminal.ini"
AUTOSTART_FILE = Path.home() / ".config" / "autostart" / "victor-startup.desktop"
DESKTOP_SHORTCUT = Path.home() / "Desktop" / "Victor Command Center.desktop"
APP_MENU_ENTRY = Path.home() / ".local" / "share" / "applications" / "victor-command-center.desktop"
ZSHRC_FILE = Path.home() / ".zshrc"


def get_baseline_source() -> Optional[Path]:
    """Find the best available baseline backup directory."""
    if BASELINE_DIR.exists() and (BASELINE_DIR / "xsettings.xml").exists():
        return BASELINE_DIR
    if REPO_BASELINE_DIR.exists() and (REPO_BASELINE_DIR / "xsettings.xml").exists():
        return REPO_BASELINE_DIR
    return None


def restore_system_file(src: Path, dest: Path) -> bool:
    """Safely restore a single system configuration file."""
    if not src.exists():
        print(f"[SKIP] Source file {src} not found.")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"[RESTORED] {src.name} -> {dest}")
    return True


def restore_factory_desktop() -> bool:
    """Restore the original Kali desktop configuration from baseline."""
    baseline = get_baseline_source()
    if not baseline:
        print("[ERROR] Factory baseline backup directory not found!")
        return False

    print("\n=======================================================")
    print(" RESTORING ORIGINAL KALI LINUX DESKTOP CONFIGURATIONS ")
    print("=======================================================")

    success = True
    # Restore XFCE configs
    xfce_files = ["xsettings.xml", "xfwm4.xml", "xfce4-desktop.xml", "xfce4-panel.xml"]
    for fname in xfce_files:
        src = baseline / fname
        dest = XFCE_PERCHANNEL_DIR / fname
        if not restore_system_file(src, dest):
            success = False

    # Restore QTerminal config
    qterm_src = baseline / "qterminal.ini"
    if qterm_src.exists():
        restore_system_file(qterm_src, QTERMINAL_CONFIG)

    # Disable / remove startup animation autostart
    if AUTOSTART_FILE.exists():
        try:
            AUTOSTART_FILE.unlink()
            print(f"[REMOVED] Disabled startup autostart: {AUTOSTART_FILE}")
        except Exception as e:
            print(f"[WARN] Could not remove autostart file: {e}")

    # Remove zsh cyberpunk hook if present in .zshrc
    if ZSHRC_FILE.exists():
        try:
            with open(ZSHRC_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            marker = "# >>> Victor Command Center Cyberpunk Prompt >>>"
            end_marker = "# <<< Victor Command Center Cyberpunk Prompt <<<"
            if marker in content and end_marker in content:
                before = content.split(marker)[0]
                after = content.split(end_marker)[1]
                with open(ZSHRC_FILE, "w", encoding="utf-8") as f:
                    f.write(before.rstrip() + "\n" + after.lstrip())
                print(f"[CLEANED] Removed cyberpunk prompt integration from {ZSHRC_FILE}")
        except Exception as e:
            print(f"[WARN] Could not clean {ZSHRC_FILE}: {e}")

    # Remove custom GTK CSS to restore native styling
    gtk_css = Path.home() / ".config" / "gtk-3.0" / "gtk.css"
    if gtk_css.exists():
        try:
            gtk_css.unlink()
            print(f"[REMOVED] Custom GTK3 CSS: {gtk_css}")
        except Exception:
            pass

    # Stop and disable Conky widget
    conky_autostart = Path.home() / ".config" / "autostart" / "victor-conky.desktop"
    if conky_autostart.exists():
        try:
            conky_autostart.unlink()
            print(f"[REMOVED] Disabled Conky autostart: {conky_autostart}")
        except Exception:
            pass
    import subprocess
    subprocess.run(["pkill", "-x", "conky"], check=False)

    # Live reload of desktop session back to Kali-Slate-Dark
    env = {**os.environ, "DISPLAY": ":0", "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus"}
    try:
        subprocess.run(["xfconf-query", "-c", "xfwm4", "-p", "/general/theme", "-s", "Kali-Slate-Dark"], env=env, check=False)
        subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "-s", "Kali-Slate-Dark"], env=env, check=False)
        subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", "-s", "Windows-10-Icons"], env=env, check=False)
        subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitorLVDS-1/workspace0/last-image", "-s", "/home/alpha/Pictures/server.png"], env=env, check=False)
        subprocess.run(["xfce4-panel", "--restart"], env=env, timeout=3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["xfdesktop", "--reload"], env=env, timeout=3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[OK] Live XFCE desktop session reloaded to stock Kali appearance.")
    except Exception:
        pass

    print("\n[OK] Original Kali desktop settings successfully restored.")
    return success


def restore_last_snapshot() -> bool:
    """Revert configuration to the most recent timestamped snapshot."""
    backups = sorted(BACKUP_DIR.glob("config_*.json"), key=os.path.getmtime, reverse=True)
    if not backups:
        print("[ERROR] No configuration backups available to restore.")
        return False

    latest = backups[0]
    print(f"[RESTORE] Reverting to latest snapshot: {latest.name}")
    from config import restore_backup
    restore_backup(latest)
    print(f"[OK] Configuration restored from {latest.name}")
    return True


def restore_specific_snapshot(snapshot_name: str) -> bool:
    """Revert configuration to a specifically named snapshot."""
    target = BACKUP_DIR / snapshot_name
    if not target.exists():
        # Try finding partial name
        matches = list(BACKUP_DIR.glob(f"*{snapshot_name}*"))
        if matches:
            target = matches[0]
        else:
            print(f"[ERROR] Snapshot '{snapshot_name}' not found in {BACKUP_DIR}")
            return False

    print(f"[RESTORE] Reverting to snapshot: {target.name}")
    from config import restore_backup
    restore_backup(target)
    print(f"[OK] Configuration successfully restored from {target.name}")
    return True


def uninstall_command_center() -> bool:
    """Completely uninstall Command Center desktop components while preserving user work."""
    print("\n=======================================================")
    print(" UNINSTALLING VICTOR COMMAND CENTER DESKTOP INTEGRATIONS")
    print("=======================================================")

    # 1. Restore original desktop settings first
    restore_factory_desktop()

    # 2. Remove desktop shortcuts
    for link in [DESKTOP_SHORTCUT, APP_MENU_ENTRY]:
        if link.exists():
            try:
                link.unlink()
                print(f"[REMOVED] Launcher: {link}")
            except Exception as e:
                print(f"[WARN] Failed to remove {link}: {e}")

    print("\n[OK] Command Center integrations cleanly removed. Workspace preserved.")
    return True


def list_backups_cli() -> None:
    """Print available backup snapshots to terminal."""
    from config import list_backups
    backups = list_backups()
    if not backups:
        print("No snapshots found in backup directory.")
        return

    print("\nAvailable Configuration Snapshots:")
    print("-" * 75)
    print(f"{'Filename':<35} {'Timestamp':<22} {'Size':<10}")
    print("-" * 75)
    for b in backups:
        size_str = f"{b['size_bytes']} B"
        print(f"{b['filename']:<35} {b['timestamp']:<22} {size_str:<10}")
    print("-" * 75)


def main():
    parser = argparse.ArgumentParser(description="Victor Command Center - Restoration & Rollback Tool")
    parser.add_argument("--list", action="store_true", help="List all available configuration backups")
    parser.add_argument("--revert-last", action="store_true", help="Revert to the most recent backup")
    parser.add_argument("--snapshot", type=str, help="Revert to a specific snapshot filename")
    parser.add_argument("--factory-reset", action="store_true", help="Restore factory stock Kali desktop settings")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall Command Center and restore stock desktop")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    if args.list:
        list_backups_cli()
        return

    if args.revert_last:
        restore_last_snapshot()
        return

    if args.snapshot:
        restore_specific_snapshot(args.snapshot)
        return

    if args.factory_reset:
        if not args.yes:
            confirm = input("Are you sure you want to restore original Kali desktop settings? [y/N]: ")
            if confirm.lower() not in ["y", "yes"]:
                print("Operation cancelled.")
                return
        restore_factory_desktop()
        return

    if args.uninstall:
        if not args.yes:
            confirm = input("Are you sure you want to uninstall Command Center desktop components? [y/N]: ")
            if confirm.lower() not in ["y", "yes"]:
                print("Operation cancelled.")
                return
        uninstall_command_center()
        return

    parser.print_help()


if __name__ == "__main__":
    main()

