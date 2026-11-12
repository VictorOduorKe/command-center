# Restoration & Safety Guide — Victor's Cyberpunk Linux Workstation

## Safety Philosophy

All desktop modifications adhere strictly to non-destructive principles:
1. No root system files or package managers are altered.
2. Complete snapshots of original XFCE configurations are preserved in `~/.config/victor-command-center/backups/factory_baseline/` and repository storage `config/factory_baseline/`.
3. User files, code repositories, and credentials are completely untouched during any restoration.

---

## 1. Restoring Original Kali Linux Desktop Appearance

To immediately revert the actual desktop back to stock Kali Linux:
```bash
vcc-restore --factory-reset
```
Or directly from the **Victor Command Center GUI**:
1. Open Command Center (`vcc`).
2. Navigate to the **Backups & Restore** tab.
3. Under *Factory Desktop Restoration Options*, click **Restore Original Desktop**.

### What this operation does:
- Restores original XFCE XML settings (`xsettings.xml`, `xfwm4.xml`, `xfce4-desktop.xml`, `xfce4-panel.xml`).
- Reverts GTK theme to `Kali-Slate-Dark`.
- Reverts Icon theme to `Windows-10-Icons`.
- Restores original wallpaper (`/home/alpha/Pictures/server.png`).
- Restores original dual full-width XFCE panels.
- Reverts QTerminal color scheme to stock `Kali-Dark`.
- Disables and stops the Conky desktop widget (`pkill conky` and removes autostart).
- Removes custom GTK3 CSS from `~/.config/gtk-3.0/gtk.css`.
- Removes post-login startup autostart animation.
- Restores the live desktop session in real-time.

---

## 2. Reverting to Previous Theme / Configuration Snapshot

If you made recent profile, skill, or theme adjustments and want to roll back to the last known working state:
```bash
vcc-restore --revert-last
```
Or to view all available timestamped snapshots:
```bash
vcc-restore --list
```
To restore a specific snapshot by filename:
```bash
vcc-restore --snapshot config_update_20261112_093000.json
```

---

## 3. Complete Uninstallation

To completely remove Victor Command Center and all associated desktop configurations while retaining all personal files:
```bash
vcc-restore --uninstall
```
This restores the factory Kali desktop, removes desktop shortcuts, removes application menu entries, and deletes autostart hooks.
