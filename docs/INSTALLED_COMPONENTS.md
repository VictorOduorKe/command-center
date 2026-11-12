# Installed Components & Architecture

## System Architecture

```
+---------------------------------------------------------------------------------+
|                       VICTOR COMMAND CENTER ARCHITECTURE                        |
+---------------------------------------------------------------------------------+
|                                                                                 |
|   +-----------------------+     +--------------------+   +-------------------+  |
|   | Victor Command Center |     | Cyberpunk Desktop  |   | Cyberpunk Startup |  |
|   |  Management GUI (Qt6) |     | HUD / Dashboard    |   | Animation (Qt6)   |  |
|   +-----------+-----------+     +---------+----------+   +---------+---------+  |
|               |                           |                        |            |
|               +---------------------+     |                        |            |
|                                     v     v                        v            |
|                     +----------------------------------+                        |
|                     | Unified Profile & Settings Store |                        |
|                     |   (~/.config/victor-command-     |                        |
|                     |    center/config.json)           |                        |
|                     +-----------------+----------------+                        |
|                                       |                                         |
|                                       v                                         |
|                     +----------------------------------+                        |
|                     | Atomic Backups & Rollback Engine |                        |
|                     |   (~/.config/victor-command-     |                        |
|                     |    center/backups/)              |                        |
|                     +-----------------+----------------+                        |
|                                       |                                         |
|                     +-----------------+----------------+                        |
|                     |                                  |                        |
|                     v                                  v                        |
|         +-----------------------+          +-----------------------+            |
|         | XFCE / System Configs |          | Terminal & Shell      |            |
|         | - xfconf / xsettings  |          | - QTerminal scheme    |            |
|         | - xfwm4 theme / panel |          | - Custom ZSH prompt   |            |
|         | - Wallpaper & Icons   |          | - Git & System info   |            |
|         +-----------------------+          +-----------------------+            |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

## Core Components

1. **Victor Command Center Management GUI (`victor-command-center`)**:
   - Modern cyberpunk control panel written in Python + PyQt6.
   - Modules:
     - **Profile Manager**: Name, Title, Bio, Education, Socials, Projects, Motto.
     - **Skills Matrix**: Categorized tech stack (Frontend, Backend, Databases, Networking, Cybersecurity, Cloud, Blockchain) with realistic proficiency indicators.
     - **Learning Tracker**: Focus tracks (Ethereum, Solidity, Smart Contracts, Web3, Cybersecurity).
     - **Startup Editor**: Interactive controls for welcome messages, system check triggers, speed, typing effects, duration, and live preview.
     - **Theme Engine**: Real-time cyberpunk theme switcher (Cyberpunk Green, Cyberpunk Blue, Matrix Dark, Minimal Hacker), custom color pickers, font options, and panel transparency.
     - **Backup & Restore Hub**: Automatic timestamped snapshots, history viewer, differential comparison, one-click rollback, and factory Kali desktop restore.

2. **Personalized Cyberpunk Desktop Dashboard / HUD**:
   - Lightweight desktop overlay widget built in Python + PyQt6 (frameless, background transparent, desktop pinned).
   - Real-time hardware monitoring reading directly from `/proc/stat`, `/proc/meminfo`, `/proc/net/dev`, `/sys/class/thermal`, and `statvfs` (0 fabricated metrics, true zero-overhead polling).
   - Display sections: Identity panel, Technical skills, Learning progress, Live system gauges, Quick developer shortcuts.

3. **Futuristic Post-Login Startup Experience**:
   - Non-blocking, cinematic cyberpunk boot sequence triggered post-login.
   - Shows Victor Oduor identity, system initialization, kernel & memory checks, typing simulation, and progress bar.
   - Instant escape shortcut (`Esc` key or click to dismiss immediately) guaranteeing zero disruption to workflow.

4. **Terminal & Shell Cyberpunk Customization**:
   - QTerminal Cyberpunk color scheme (neon green `#00ff66`, electric cyan `#00e5ff`, subtle blue `#1e3a8a`, matte black `#0d0e15`).
   - Custom prompt configuration with Git branch, current working directory, execution status, and clean styling.

