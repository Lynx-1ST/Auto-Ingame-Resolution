
# Auto Resolution Switcher (WMI)

A lightweight Windows tray utility that automatically changes the screen resolution when a specific game starts and restores the previous resolution when the game exits.
This version uses **WMI process events** instead of polling, resulting in lower CPU usage and faster detection.

---

## Features

* Automatically detects game start and exit
* Switches to a custom resolution when the game launches
* Restores the previous resolution after the game closes
* Saves configuration to `config.json`
* Small system tray application
* Debug log window
* Embedded NirCmd (no separate installation required)
* Low CPU usage (event-driven monitoring)

---

## How It Works

The program listens to Windows process events using WMI:

* `Win32_ProcessStartTrace`
* `Win32_ProcessStopTrace`

Workflow:

1. Wait for the game process to start
2. Change resolution to the configured value
3. Wait for the process to exit
4. Restore the original resolution automatically

---

## Screenshot / UI

Tray menu includes:

* Show Debug Log
* Save current resolution
* Restore saved resolution
* Set game resolution
* Exit

---

## Requirements (Python)

Python 3.9+

Install dependencies:

```bash
pip install pystray pillow pywin32 wmi
```

---

## Build EXE

Using PyInstaller:

```bash
pyinstaller --onefile --noconsole --icon=icon.ico main.py
```

Optional (embed icon properly in tray and exe):

```bash
pyinstaller --onefile --noconsole --icon=icon.ico --add-data "icon.ico;." main.py
```

---

## Config File

The program automatically creates:

```
config.json
```

Example:

```json
{
  "game_resolution": [1440, 1080, 32, 240],
  "last_user_resolution": [1920, 1080, 32, 144]
}
```

---

## Customization

Edit these values in the source:

```python
GAME_PROCESS = "DeltaForceClient-Win64-Shipping.exe"
```

You can change this to any game executable.

---

## Safety Notes

This tool:

* does not inject into games
* does not modify memory
* does not hook DirectX or graphics drivers
* only monitors Windows process events and changes display settings
* use with caution
Behavior is similar to normal desktop utilities that adjust resolution.

---

## Known Limitations

* Some GPUs or monitors may reject unsupported resolutions
* Certain games force resolution internally and may override system settings
* Requires administrator privileges in some Windows configurations

---

## Project Structure

```
main.py
icon.ico
config.json (auto-created)
```

---

## License

MIT License

---
