import os
import sys
import json
import threading
import queue
import time
import base64
import tempfile
import subprocess

import pystray
from pystray import MenuItem as Item
from PIL import Image
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

import win32api
import win32con

import pythoncom
import wmi


# ========================= CONFIG FILE =========================
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config():
    data = {
        "game_resolution": RES_GAME,
        "last_user_resolution": last_user_resolution,
    }
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
        log("Config saved")
    except Exception as e:
        log(f"[ERR] Save config failed: {e}")

config_data = load_config()


# ========================= EMBEDDED NIRCMD =========================
NIRCMD_B64 = r""  # paste base64 ở đây

def ensure_nircmd():
    temp_dir = os.path.join(tempfile.gettempdir(), "auto_res_nircmd")
    os.makedirs(temp_dir, exist_ok=True)
    nircmd_path = os.path.join(temp_dir, "nircmd.exe")

    if not os.path.exists(nircmd_path):
        try:
            data = base64.b64decode(NIRCMD_B64)
            with open(nircmd_path, "wb") as f:
                f.write(data)
            print("[OK] Extracted nircmd.exe")
        except Exception as e:
            print(f"[ERR] Decode nircmd failed: {e}")
            return None
    return nircmd_path


# ========================= RESOLUTION =========================
def get_current_resolution():
    devmode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
    return (
        devmode.PelsWidth,
        devmode.PelsHeight,
        devmode.BitsPerPel,
        devmode.DisplayFrequency,
    )

def set_resolution(width, height, color_bits, refresh):
    nircmd = ensure_nircmd()
    if not nircmd:
        log("[ERR] nircmd not available")
        return False

    cmd = [nircmd, "setdisplay", str(width), str(height), str(color_bits), str(refresh)]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        log(f"[OK] setdisplay {width}x{height}@{refresh}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"[ERR] nircmd error: {e}")
        return False


# ========================= CONFIG =========================
GAME_PROCESS = "DeltaForceClient-Win64-Shipping.exe"

RES_GAME = config_data.get(
    "game_resolution",
    [1440, 1080, 32, get_current_resolution()[3]]
)

last_user_resolution = config_data.get("last_user_resolution", None)


# ========================= LOG =========================
log_queue = queue.Queue()

def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    log_queue.put(line)
    print(line)


# ========================= STATE =========================
stop_event = threading.Event()
game_active = False
original_resolution = get_current_resolution()


# ========================= WMI WATCHER =========================
def wmi_worker():
    global game_active

    pythoncom.CoInitialize()
    c = wmi.WMI()

    log(f"WMI watching {GAME_PROCESS}")

    start_watcher = c.Win32_ProcessStartTrace.watch_for()
    stop_watcher = c.Win32_ProcessStopTrace.watch_for()

    while not stop_event.is_set():

        # START EVENT
        try:
            event = start_watcher(timeout_ms=500)
            if event and event.ProcessName == GAME_PROCESS:
                if not game_active:
                    log("Game detected (WMI)")
                    set_resolution(*RES_GAME)
                    game_active = True
        except wmi.x_wmi_timed_out:
            pass
        except Exception as e:
            log(f"WMI start error: {e}")

        # STOP EVENT
        try:
            event = stop_watcher(timeout_ms=500)
            if event and event.ProcessName == GAME_PROCESS:
                if game_active:
                    log("Game closed -> restoring original")
                    set_resolution(*original_resolution)
                    game_active = False
        except wmi.x_wmi_timed_out:
            pass
        except Exception as e:
            log(f"WMI stop error: {e}")

    log("WMI watcher stopped")


# ========================= DEBUG WINDOW =========================
debug_window = None

def open_debug_window():
    global debug_window

    if debug_window and debug_window.winfo_exists():
        debug_window.lift()
        return

    root = tk.Tk()
    root.title("Debug Log")
    root.geometry("800x500")

    text = ScrolledText(root, state="disabled", font=("Consolas", 9))
    text.pack(fill="both", expand=True)

    def poll_log():
        while True:
            try:
                line = log_queue.get_nowait()
            except queue.Empty:
                break
            text.configure(state="normal")
            text.insert("end", line + "\n")
            text.see("end")
            text.configure(state="disabled")
        root.after(200, poll_log)

    root.after(200, poll_log)

    def on_close():
        root.withdraw()

    root.protocol("WM_DELETE_WINDOW", on_close)
    debug_window = root
    root.mainloop()


# ========================= CUSTOM GAME RESOLUTION =========================
def open_custom_resolution():
    def apply():
        try:
            w = int(entry_w.get())
            h = int(entry_h.get())
            hz = int(entry_hz.get())

            RES_GAME[0] = w
            RES_GAME[1] = h
            RES_GAME[2] = 32
            RES_GAME[3] = hz

            save_config()
            log(f"[CONFIG] Game resolution set to {w}x{h}@{hz}")
            win.destroy()
        except:
            log("[ERR] Invalid input")

    win = tk.Tk()
    win.title("Game Resolution")
    win.geometry("260x200")
    win.resizable(False, False)

    tk.Label(win, text="Resolution used when game starts").pack(pady=5)

    tk.Label(win, text="Width").pack()
    entry_w = tk.Entry(win)
    entry_w.insert(0, str(RES_GAME[0]))
    entry_w.pack()

    tk.Label(win, text="Height").pack()
    entry_h = tk.Entry(win)
    entry_h.insert(0, str(RES_GAME[1]))
    entry_h.pack()

    tk.Label(win, text="Refresh rate").pack()
    entry_hz = tk.Entry(win)
    entry_hz.insert(0, str(RES_GAME[3]))
    entry_hz.pack()

    tk.Button(win, text="Save", command=apply).pack(pady=10)

    win.mainloop()


# ========================= MENU ACTIONS =========================
def on_restore_current(icon, item):
    global last_user_resolution
    res = get_current_resolution()
    last_user_resolution = res
    save_config()
    log(f"Saved current resolution {res}")

def on_restore_saved(icon, item):
    if last_user_resolution:
        set_resolution(*last_user_resolution)
    else:
        log("No saved resolution")

def on_custom(icon, item):
    threading.Thread(target=open_custom_resolution, daemon=True).start()

def on_show_debug(icon, item):
    threading.Thread(target=open_debug_window, daemon=True).start()

def on_exit(icon, item):
    stop_event.set()
    icon.stop()


# ========================= TRAY =========================
def create_tray_icon():
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_dir, "icon.ico")

    try:
        image = Image.open(icon_path)
    except:
        image = Image.new('RGB', (64, 64), color='#4CAF50')

    menu = (
        Item("Show Debug", on_show_debug),

        Item("Resolution", pystray.Menu(
            Item("Save current as restore point", on_restore_current),
            Item("Restore saved resolution", on_restore_saved),
            Item("Set game resolution...", on_custom),
        )),

        Item("Exit", on_exit),
    )

    icon = pystray.Icon("AutoRes", image, "Auto Resolution Monitor", menu)
    icon.run()


# ========================= MAIN =========================
def main():
    ensure_nircmd()

    wmi_thread = threading.Thread(target=wmi_worker, daemon=True)
    wmi_thread.start()

    log("Started (WMI mode)")
    create_tray_icon()

    stop_event.set()
    wmi_thread.join(timeout=3)

    log("Exited cleanly")


if __name__ == "__main__":
    main()
