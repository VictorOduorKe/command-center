#!/usr/bin/env python3
"""
Victor Command Center - Configuration & Backup Engine
Manages profile, theme, startup settings, atomic saves, and timestamped backups.
"""

import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CONFIG_DIR = Path.home() / ".config" / "victor-command-center"
CONFIG_FILE = CONFIG_DIR / "config.json"
BACKUP_DIR = CONFIG_DIR / "backups"
MAX_BACKUPS = 20

DEFAULT_CONFIG: Dict[str, Any] = {
    "version": "1.0.0",
    "profile": {
        "name": "Victor Oduor",
        "title": "Software Developer & ICT Professional",
        "institution": "Technical University of Mombasa",
        "degree": "Bachelor of Information and Communication Technology",
        "github": "https://github.com/VictorOduorKe",
        "linkedin": "https://www.linkedin.com/in/Victor-Oduor-ke/",
        "motto": "Building secure, decentralized, and scalable digital solutions.",
        "bio": "Passionate software developer and ICT professional dedicated to building modern web applications, robust network infrastructure, and exploring blockchain technologies."
    },
    "skills": [
        {"name": "React", "category": "Frontend", "level": "established", "proficiency": 85},
        {"name": "JavaScript", "category": "Frontend", "level": "established", "proficiency": 88},
        {"name": "HTML5 / CSS3", "category": "Frontend", "level": "established", "proficiency": 92},
        {"name": "Laravel & PHP", "category": "Backend", "level": "established", "proficiency": 90},
        {"name": "Node.js", "category": "Backend", "level": "established", "proficiency": 80},
        {"name": "RESTful APIs", "category": "Backend", "level": "established", "proficiency": 88},
        {"name": "MySQL", "category": "Databases", "level": "established", "proficiency": 86},
        {"name": "MongoDB", "category": "Databases", "level": "established", "proficiency": 78},
        {"name": "Linux Administration", "category": "Networking", "level": "established", "proficiency": 85},
        {"name": "Networking & IT Support", "category": "Networking", "level": "established", "proficiency": 82},
        {"name": "Cybersecurity Fundamentals", "category": "Cybersecurity", "level": "established", "proficiency": 75},
        {"name": "Kali Linux Tools & Auditing", "category": "Cybersecurity", "level": "learning", "proficiency": 70},
        {"name": "Cloud Foundations & Docker", "category": "Cloud", "level": "learning", "proficiency": 68},
        {"name": "Ethereum Fundamentals", "category": "Blockchain", "level": "learning", "proficiency": 60},
        {"name": "Solidity Programming", "category": "Blockchain", "level": "learning", "proficiency": 55},
        {"name": "Smart Contract Testing & Web3", "category": "Blockchain", "level": "future_goal", "proficiency": 40}
    ],
    "learning_goals": [
        {"topic": "Ethereum & EVM Architecture", "progress": 65, "status": "In Progress"},
        {"topic": "Solidity Smart Contract Development", "progress": 55, "status": "In Progress"},
        {"topic": "Smart Contract Testing & Security Audits", "progress": 40, "status": "In Progress"},
        {"topic": "Web3 Frontend Integration (ethers.js / wagmi)", "progress": 35, "status": "Planned"},
        {"topic": "Advanced Linux Hardening & Penetration Testing", "progress": 70, "status": "In Progress"}
    ],
    "projects": [
        {
            "name": "Victor Command Center",
            "description": "Futuristic Cyberpunk Linux Workstation Dashboard & Desktop Management Suite",
            "tech": "Python, PyQt6, XFCE4, Linux Kernel /proc",
            "url": "https://github.com/VictorOduorKe"
        },
        {
            "name": "Enterprise Web Applications",
            "description": "Secure full-stack responsive management and analytics platforms",
            "tech": "Laravel, React, Node.js, MySQL",
            "url": "https://github.com/VictorOduorKe"
        },
        {
            "name": "Web3 & Smart Contract Research",
            "description": "Decentralized applications, Solidity smart contracts and verification tools",
            "tech": "Solidity, Ethereum, Hardhat, Ethers.js",
            "url": "https://github.com/VictorOduorKe"
        }
    ],
    "theme": {
        "preset": "Cyberpunk Green",
        "primary_bg": "#0a0b10",
        "secondary_bg": "#12161f",
        "primary_accent": "#00ff66",
        "secondary_accent": "#00e5ff",
        "subtle_accent": "#0077ff",
        "text_color": "#e0f8ff",
        "font_family": "FiraCode, Monospace",
        "font_size": 10,
        "panel_transparency": 88,
        "animation_intensity": "medium"
    },
    "startup": {
        "enabled": True,
        "duration_ms": 3800,
        "animation_speed": 1.0,
        "typing_effect": True,
        "show_system_info": True,
        "welcome_message": "CYBERPUNK WORKSTATION INITIALIZED",
        "messages": [
            "[SYS_INIT] Loading Linux kernel subsystems...",
            "[CPU_INFO] Intel(R) Core(TM) i5-2520M verified (4 threads)",
            "[MEM_CHK] 8.0 GB RAM initialized, swap ready",
            "[NET_MGR] Network interface stack active",
            "[SEC_AUD] Kali Linux security toolkit loaded",
            "[DEV_ENV] Workspace and developer toolchains mounted",
            "[BLOCKCHAIN] Web3 development environment initialized",
            "[AUTH] Welcome back, Victor Oduor. System ready."
        ]
    },
    "shortcuts": [
        {"name": "Terminal", "command": "qterminal", "icon": "utilities-terminal"},
        {"name": "File Manager", "command": "thunar", "icon": "system-file-manager"},
        {"name": "Antigravity IDE", "command": "antigravity", "icon": "accessories-text-editor"},
        {"name": "Mousepad", "command": "mousepad", "icon": "accessories-text-editor"},
        {"name": "Browser", "command": "chromium", "icon": "web-browser"},
        {"name": "Bruno API", "command": "bruno", "icon": "network-wired"},
        {"name": "Wireshark", "command": "wireshark", "icon": "wireshark"},
        {"name": "Command Center", "command": "python3 /home/alpha/victor-command-center/src/main.py", "icon": "preferences-system"}
    ]
}


THEME_PRESETS: Dict[str, Dict[str, Any]] = {
    "Cyberpunk Green": {
        "primary_bg": "#0a0b10",
        "secondary_bg": "#12161f",
        "primary_accent": "#00ff66",
        "secondary_accent": "#00e5ff",
        "subtle_accent": "#0077ff",
        "text_color": "#e0f8ff",
        "panel_transparency": 88
    },
    "Cyberpunk Blue": {
        "primary_bg": "#070b14",
        "secondary_bg": "#0f172a",
        "primary_accent": "#00d2ff",
        "secondary_accent": "#3b82f6",
        "subtle_accent": "#6366f1",
        "text_color": "#e2e8f0",
        "panel_transparency": 88
    },
    "Matrix Dark": {
        "primary_bg": "#040804",
        "secondary_bg": "#091409",
        "primary_accent": "#00ff41",
        "secondary_accent": "#008f11",
        "subtle_accent": "#003b00",
        "text_color": "#c4f9c4",
        "panel_transparency": 90
    },
    "Minimal Hacker": {
        "primary_bg": "#0e0e11",
        "secondary_bg": "#18181f",
        "primary_accent": "#00f0ff",
        "secondary_accent": "#ff007f",
        "subtle_accent": "#7928ca",
        "text_color": "#f1f1f1",
        "panel_transparency": 85
    }
}


def ensure_dirs() -> None:
    """Ensure required configuration and backup directories exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def validate_config(cfg: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate configuration structure and field integrity."""
    required_keys = ["profile", "skills", "learning_goals", "theme", "startup"]
    for k in required_keys:
        if k not in cfg:
            return False, f"Missing required configuration section: {k}"

    prof = cfg["profile"]
    if not prof.get("name") or not isinstance(prof.get("name"), str):
        return False, "Profile must include a valid non-empty 'name' string"

    theme = cfg["theme"]
    if not theme.get("primary_accent") or not theme.get("primary_bg"):
        return False, "Theme must include 'primary_accent' and 'primary_bg'"

    return True, "Configuration is valid"


def create_backup(label: str = "auto") -> Path:
    """Create a timestamped backup of the current configuration and return its path."""
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"config_{label}_{timestamp}.json"

    if CONFIG_FILE.exists():
        shutil.copy2(CONFIG_FILE, backup_file)
    else:
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)

    # Prune old backups exceeding MAX_BACKUPS
    all_backups = sorted(BACKUP_DIR.glob("config_*.json"), key=os.path.getmtime)
    while len(all_backups) > MAX_BACKUPS:
        oldest = all_backups.pop(0)
        try:
            oldest.unlink()
        except OSError:
            pass

    return backup_file


def list_backups() -> List[Dict[str, Any]]:
    """List all available backups sorted by modification date (newest first)."""
    ensure_dirs()
    backups = []
    for p in sorted(BACKUP_DIR.glob("config_*.json"), key=os.path.getmtime, reverse=True):
        mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        backups.append({
            "filename": p.name,
            "path": str(p),
            "timestamp": mtime,
            "size_bytes": p.stat().st_size
        })
    return backups


def load_config() -> Dict[str, Any]:
    """Load configuration from disk or initialize with defaults if not present."""
    ensure_dirs()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG, backup=False)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        valid, msg = validate_config(data)
        if not valid:
            print(f"[WARN] Invalid config loaded: {msg}. Falling back to default.")
            return DEFAULT_CONFIG.copy()
        return data
    except Exception as e:
        print(f"[ERROR] Failed to load config ({e}). Using defaults.")
        return DEFAULT_CONFIG.copy()


def save_config(cfg: Dict[str, Any], backup: bool = True, label: str = "update") -> bool:
    """Atomically save configuration with validation and automatic backup."""
    ensure_dirs()
    valid, msg = validate_config(cfg)
    if not valid:
        raise ValueError(f"Cannot save invalid configuration: {msg}")

    if backup and CONFIG_FILE.exists():
        create_backup(label=label)

    # Atomic write via temporary file
    temp_file = CONFIG_DIR / f".config_{int(time.time()*1000)}.tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_file, CONFIG_FILE)
        return True
    except Exception as e:
        if temp_file.exists():
            temp_file.unlink()
        raise IOError(f"Atomic configuration save failed: {e}")


def restore_backup(backup_path: Path) -> bool:
    """Restore configuration from a designated backup file."""
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    with open(backup_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    valid, msg = validate_config(data)
    if not valid:
        raise ValueError(f"Backup file contains invalid config: {msg}")

    # Create safety backup of current state before reverting
    create_backup(label="pre_restore")
    return save_config(data, backup=False)


if __name__ == "__main__":
    ensure_dirs()
    cfg = load_config()
    print(f"[OK] Configuration active for: {cfg['profile']['name']}")
    print(f"[OK] Skills count: {len(cfg['skills'])}")
    print(f"[OK] Active theme: {cfg['theme']['preset']}")

