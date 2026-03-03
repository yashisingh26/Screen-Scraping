import time
import threading
import mss
import numpy as np
import easyocr
import requests
from datetime import datetime
import sys

# OPTIONAL tray icon support – comment out if you don't want tray
try:
    import pystray
    from PIL import Image as PILImage
    USE_TRAY = True
except ImportError:
    USE_TRAY = False

# ======================
# CONFIG
# ======================

# Server on same PC (#1)
SERVER_URL = "http://192.168.29.30:5000/upload"

SCAN_DELAY = 3  # seconds between scans

running = True
reader = easyocr.Reader(['en'], gpu=False)


def crop_whatsapp_chat_area(frame: np.ndarray) -> np.ndarray:
    """
    Crop WhatsApp chat part based on screen ratios.
    You can adjust these if your layout is different.
    """
    h, w, _ = frame.shape

    # ignore left sidebar (~0–25%), top bar (~0–12%), and bottom input (~last ~12%)
    x1 = int(w * 0.25)
    x2 = int(w * 0.98)
    y1 = int(h * 0.12)
    y2 = int(h * 0.88)

    return frame[y1:y2, x1:x2]


def send_loop():
    global running
    last_lines = []

    with mss.mss() as sct:
        monitor = sct.monitors[1]

        while running:
            try:
                scr = sct.grab(monitor)
                frame = np.array(scr)[:, :, :3]  # drop alpha

                roi = crop_whatsapp_chat_area(frame)

                results = reader.readtext(roi, detail=0)
                lines = [t.strip() for t in results if len(t.strip()) > 1]

                # Only send if there are new lines
                new_lines = [l for l in lines if l not in last_lines]

                if new_lines:
                    payload = {
                        "timestamp": datetime.now().isoformat(),
                        "messages": new_lines
                    }
                    try:
                        r = requests.post(SERVER_URL, json=payload, timeout=3)
                        print(f"[AGENT] Sent {len(new_lines)} lines, status={r.status_code}")
                    except Exception as e:
                        print("[AGENT ERROR] sending:", e)

                    last_lines = lines

            except Exception as e:
                print("[AGENT ERROR] scan:", e)

            time.sleep(SCAN_DELAY)


def on_exit(icon=None, item=None):
    global running
    running = False
    if icon:
        icon.stop()
    sys.exit(0)


def run_tray():
    # Very simple green square as icon
    image = PILImage.new("RGB", (16, 16), "green")
    menu = pystray.Menu(pystray.MenuItem("Exit", on_exit))
    icon = pystray.Icon("SAReader", image, "Screen Reader Agent", menu)
    icon.run()


if __name__ == "__main__":
    # Start OCR sender thread
    threading.Thread(target=send_loop, daemon=True).start()

    if USE_TRAY:
        run_tray()
    else:
        print("[AGENT] Running without tray. Press Ctrl+C to stop.")
        try:
            while running:
                time.sleep(1)
        except KeyboardInterrupt:
            on_exit()
