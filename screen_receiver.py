"""
╔══════════════════════════════════════════════╗
║   LiveFeed — Screen Monitor  (PC #2 Side)    ║
║   Python + tkinter  |  Dark UI               ║
╚══════════════════════════════════════════════╝

Requirements:
    pip install requests

Run:
    python screen_receiver.py
"""

import requests
import threading
import time
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk, font
import tkinter as tk

# ──────────────────────────────────────────────
# THEME CONFIG
# ──────────────────────────────────────────────
C = {
    "bg":        "#0a0c10",
    "surface":   "#111318",
    "card":      "#161b24",
    "border":    "#1f2733",
    "accent":    "#00e5ff",
    "green":     "#22d3a5",
    "red":       "#ff4757",
    "yellow":    "#ffd32a",
    "text":      "#e2e8f0",
    "muted":     "#4a5568",
    "highlight_bg": "#ffd32a",
    "highlight_fg": "#000000",
}

# ──────────────────────────────────────────────
# STATE
# ──────────────────────────────────────────────
all_messages = []          # [{"time": "...", "msg": "..."}]
lock = threading.Lock()
fetch_thread_running = True
auto_scroll = True
is_search_mode = False
fetch_delay = 3            # seconds
server_url = "http://192.168.29.30:5000/fetch"


# ──────────────────────────────────────────────
# UTILS
# ──────────────────────────────────────────────
def parse_time(ts: str):
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        try:
            return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
        except Exception:
            return None


def filter_by_time(messages, range_name: str):
    if range_name == "All Time":
        return messages
    now = datetime.now()
    result = []
    for item in messages:
        dt = parse_time(item["time"])
        if not dt:
            continue
        if range_name == "Today":
            if dt.date() == now.date():
                result.append(item)
        elif range_name == "Yesterday":
            if dt.date() == (now.date() - timedelta(days=1)):
                result.append(item)
        elif range_name == "Last 1 Hour":
            if dt >= now - timedelta(hours=1):
                result.append(item)
        elif range_name == "Last 24 Hours":
            if dt >= now - timedelta(hours=24):
                result.append(item)
    return result


def fmt_time(ts: str) -> str:
    dt = parse_time(ts)
    if dt:
        return dt.strftime("%H:%M:%S")
    return ts[:19] if len(ts) >= 19 else ts


# ──────────────────────────────────────────────
# FETCH THREAD
# ──────────────────────────────────────────────
def fetch_loop():
    global all_messages
    while fetch_thread_running:
        try:
            r = requests.get(server_url, timeout=4)
            data = r.json()
            if isinstance(data, list):
                with lock:
                    all_messages = data
                root.after(0, on_data_received, True)
        except Exception:
            root.after(0, on_data_received, False)
        time.sleep(fetch_delay)


def on_data_received(success: bool):
    if success:
        set_status("live")
        lbl_total.config(text=f"Total: {len(all_messages)}")
        lbl_refresh.config(text=f"Updated: {datetime.now().strftime('%H:%M:%S')}")
        if not is_search_mode:
            refresh_display()
    else:
        set_status("offline")


# ──────────────────────────────────────────────
# DISPLAY
# ──────────────────────────────────────────────
def render_messages(msgs, keyword=None):
    text_box.config(state=NORMAL)
    text_box.delete("1.0", END)

    kw = (keyword or "").strip().lower()

    if not msgs:
        text_box.insert(END, "\n\n   No messages found.\n", "muted")
        text_box.config(state=DISABLED)
        lbl_shown.config(text="Shown: 0")
        lbl_match.config(text="Matches: 0" if kw else "Matches: —")
        return

    for item in msgs:
        ts_str = fmt_time(item["time"])
        msg_str = item["msg"]

        text_box.insert(END, f"  {ts_str}  ", "timestamp")

        if kw and kw in msg_str.lower():
            # Insert message with highlighted keyword
            lower_msg = msg_str.lower()
            start = 0
            while True:
                idx = lower_msg.find(kw, start)
                if idx == -1:
                    text_box.insert(END, msg_str[start:], "message")
                    break
                text_box.insert(END, msg_str[start:idx], "message")
                text_box.insert(END, msg_str[idx:idx + len(kw)], "highlight")
                start = idx + len(kw)
        else:
            text_box.insert(END, msg_str, "message")

        text_box.insert(END, "\n", "message")

    text_box.config(state=DISABLED)
    lbl_shown.config(text=f"Shown: {len(msgs)}")
    lbl_match.config(text=f"Matches: {len(msgs)}" if kw else "Matches: —")

    if auto_scroll:
        text_box.see(END)


def refresh_display():
    with lock:
        msgs = filter_by_time(all_messages, time_var.get())
    render_messages(msgs)


# ──────────────────────────────────────────────
# SEARCH
# ──────────────────────────────────────────────
def do_search(*_):
    global is_search_mode
    kw = search_var.get().strip()
    range_name = time_var.get()

    with lock:
        msgs = filter_by_time(all_messages, range_name)

    if kw:
        is_search_mode = True
        msgs = [m for m in msgs if kw.lower() in m["msg"].lower()]
        render_messages(msgs, keyword=kw)
    else:
        is_search_mode = False
        render_messages(msgs)


def clear_search():
    global is_search_mode
    is_search_mode = False
    search_var.set("")
    time_var.set("All Time")
    refresh_display()
    lbl_match.config(text="Matches: —")


# ──────────────────────────────────────────────
# STATUS
# ──────────────────────────────────────────────
def set_status(state: str):
    if state == "live":
        status_canvas.itemconfig(status_dot, fill=C["green"])
        status_label.config(text="● Live", fg=C["green"])
    else:
        status_canvas.itemconfig(status_dot, fill=C["red"])
        status_label.config(text="○ Offline", fg=C["red"])


def pulse_dot():
    """Animate the live dot."""
    if status_label.cget("text").startswith("●"):
        cur = status_canvas.itemcget(status_dot, "fill")
        nxt = C["green"] if cur != C["green"] else "#0a4a3a"
        status_canvas.itemconfig(status_dot, fill=nxt)
    root.after(800, pulse_dot)


# ──────────────────────────────────────────────
# CONFIG PANEL
# ──────────────────────────────────────────────
config_visible = False

def toggle_config():
    global config_visible
    config_visible = not config_visible
    if config_visible:
        config_frame.pack(fill=X, padx=16, pady=(0, 6))
        btn_config.config(text="⚙  Config  ▲")
    else:
        config_frame.pack_forget()
        btn_config.config(text="⚙  Config  ▼")


def apply_config():
    global server_url, fetch_delay
    url = cfg_url_var.get().strip()
    try:
        delay = int(cfg_delay_var.get())
    except ValueError:
        delay = 3
    if url:
        server_url = url
    fetch_delay = max(1, delay)
    cfg_status.config(text="✓ Applied!", fg=C["green"])
    root.after(2000, lambda: cfg_status.config(text=""))


# ──────────────────────────────────────────────
# SCROLL HELPERS
# ──────────────────────────────────────────────
def scroll_bottom():
    text_box.see(END)


def scroll_top():
    text_box.see("1.0")


def copy_all():
    with lock:
        content = "\n".join(f"[{m['time']}] {m['msg']}" for m in all_messages)
    root.clipboard_clear()
    root.clipboard_append(content)
    btn_copy.config(text="✓ Copied!")
    root.after(1500, lambda: btn_copy.config(text="Copy All"))


def toggle_autoscroll():
    global auto_scroll
    auto_scroll = not auto_scroll
    btn_autoscroll.config(
        text="Auto-scroll: ON" if auto_scroll else "Auto-scroll: OFF",
        fg=C["green"] if auto_scroll else C["muted"],
    )


# ──────────────────────────────────────────────
# BUILD GUI
# ──────────────────────────────────────────────
root = tk.Tk()
root.title("LiveFeed — Screen Monitor")
root.geometry("1020x720")
root.configure(bg=C["bg"])
root.minsize(750, 520)

# Fonts
FONT_MONO   = ("Courier New", 10)
FONT_MONO_B = ("Courier New", 10, "bold")
FONT_HEAD   = ("Courier New", 16, "bold")
FONT_LABEL  = ("Courier New", 9)
FONT_BTN    = ("Courier New", 9, "bold")
FONT_SMALL  = ("Courier New", 8)

# ── Header ──────────────────────────────────────
header_frame = Frame(root, bg=C["card"], pady=12)
header_frame.pack(fill=X, padx=0, pady=(0, 0))

Frame(header_frame, bg=C["border"], height=1).pack(fill=X, side=BOTTOM)

inner_header = Frame(header_frame, bg=C["card"])
inner_header.pack(fill=X, padx=16)

lbl_title = Label(inner_header, text="📡  LiveFeed Monitor",
                  font=FONT_HEAD, bg=C["card"], fg=C["accent"])
lbl_title.pack(side=LEFT)

lbl_subtitle = Label(inner_header, text="  PC#1 → PC#2  screen receiver",
                     font=FONT_LABEL, bg=C["card"], fg=C["muted"])
lbl_subtitle.pack(side=LEFT, padx=(0, 20), anchor=S, pady=(0, 2))

# Right side of header — status
right_header = Frame(inner_header, bg=C["card"])
right_header.pack(side=RIGHT)

lbl_refresh = Label(right_header, text="Updated: —",
                    font=FONT_SMALL, bg=C["card"], fg=C["muted"])
lbl_refresh.pack(side=RIGHT, padx=(10, 0))

status_label = Label(right_header, text="○ Offline",
                     font=FONT_BTN, bg=C["card"], fg=C["red"])
status_label.pack(side=RIGHT)

status_canvas = Canvas(right_header, width=1, height=1, bg=C["card"],
                       highlightthickness=0)
status_canvas.pack(side=RIGHT)
status_dot = status_canvas.create_oval(0, 0, 0, 0, fill=C["red"], outline="")

# ── Config Toggle ────────────────────────────────
btn_config = Button(root, text="⚙  Config  ▼",
                    font=FONT_LABEL, bg=C["surface"], fg=C["muted"],
                    bd=0, padx=16, pady=6,
                    activebackground=C["card"], activeforeground=C["text"],
                    cursor="hand2", command=toggle_config)
btn_config.pack(fill=X)

# ── Config Panel (hidden by default) ────────────
config_frame = Frame(root, bg=C["card"], pady=12)
# not packed yet

cfg_inner = Frame(config_frame, bg=C["card"])
cfg_inner.pack(fill=X, padx=16)

Label(cfg_inner, text="Server URL:", font=FONT_LABEL,
      bg=C["card"], fg=C["muted"]).grid(row=0, column=0, sticky=W, padx=(0, 8))
cfg_url_var = StringVar(value=server_url)
Entry(cfg_inner, textvariable=cfg_url_var, font=FONT_MONO,
      bg=C["surface"], fg=C["text"], insertbackground=C["accent"],
      relief=FLAT, width=42,
      highlightthickness=1, highlightcolor=C["accent"],
      highlightbackground=C["border"]).grid(row=0, column=1, padx=(0, 16))

Label(cfg_inner, text="Poll (sec):", font=FONT_LABEL,
      bg=C["card"], fg=C["muted"]).grid(row=0, column=2, padx=(0, 8))
cfg_delay_var = StringVar(value=str(fetch_delay))
Entry(cfg_inner, textvariable=cfg_delay_var, font=FONT_MONO,
      bg=C["surface"], fg=C["text"], insertbackground=C["accent"],
      relief=FLAT, width=5,
      highlightthickness=1, highlightcolor=C["accent"],
      highlightbackground=C["border"]).grid(row=0, column=3, padx=(0, 10))

Button(cfg_inner, text="Apply", font=FONT_BTN,
       bg=C["accent"], fg="#000", relief=FLAT, padx=12, pady=4,
       activebackground="#00b8cc", cursor="hand2",
       command=apply_config).grid(row=0, column=4, padx=(0, 10))

cfg_status = Label(cfg_inner, text="", font=FONT_LABEL,
                   bg=C["card"], fg=C["green"])
cfg_status.grid(row=0, column=5, sticky=W)

# ── Controls ────────────────────────────────────
ctrl_frame = Frame(root, bg=C["surface"], pady=10)
ctrl_frame.pack(fill=X, padx=0)
Frame(root, bg=C["border"], height=1).pack(fill=X)

ctrl_inner = Frame(ctrl_frame, bg=C["surface"])
ctrl_inner.pack(fill=X, padx=16)

# Search label
Label(ctrl_inner, text="SEARCH", font=FONT_SMALL,
      bg=C["surface"], fg=C["muted"]).grid(row=0, column=0, sticky=W, padx=(0, 6))

search_var = StringVar()
search_var.trace_add("write", lambda *_: do_search())
search_entry = Entry(ctrl_inner, textvariable=search_var, font=FONT_MONO,
                     bg=C["card"], fg=C["text"], insertbackground=C["accent"],
                     relief=FLAT, width=34,
                     highlightthickness=1, highlightcolor=C["accent"],
                     highlightbackground=C["border"])
search_entry.grid(row=0, column=1, padx=(0, 16), ipady=5)

Label(ctrl_inner, text="TIME", font=FONT_SMALL,
      bg=C["surface"], fg=C["muted"]).grid(row=0, column=2, padx=(0, 6))

time_var = StringVar(value="All Time")
time_menu = ttk.Combobox(ctrl_inner, textvariable=time_var, font=FONT_MONO,
                         values=["All Time", "Today", "Yesterday",
                                 "Last 1 Hour", "Last 24 Hours"],
                         state="readonly", width=14)
time_menu.grid(row=0, column=3, padx=(0, 10))
time_menu.bind("<<ComboboxSelected>>", do_search)

# Style combobox
style = ttk.Style()
style.theme_use("default")
style.configure("TCombobox",
                fieldbackground=C["card"],
                background=C["card"],
                foreground=C["text"],
                arrowcolor=C["muted"],
                bordercolor=C["border"],
                lightcolor=C["border"],
                darkcolor=C["border"],
                selectbackground=C["card"],
                selectforeground=C["text"])

Button(ctrl_inner, text="Search", font=FONT_BTN,
       bg=C["accent"], fg="#000", relief=FLAT, padx=14, pady=5,
       activebackground="#00b8cc", cursor="hand2",
       command=do_search).grid(row=0, column=4, padx=(0, 6))

Button(ctrl_inner, text="Clear", font=FONT_BTN,
       bg=C["card"], fg=C["muted"], relief=FLAT, padx=12, pady=5,
       activebackground=C["border"], activeforeground=C["text"],
       cursor="hand2", command=clear_search).grid(row=0, column=5)

# ── Stats Row ───────────────────────────────────
stats_frame = Frame(root, bg=C["bg"], pady=6)
stats_frame.pack(fill=X, padx=16)

stats_inner = Frame(stats_frame, bg=C["bg"])
stats_inner.pack(side=LEFT, fill=X)

def stat_chip(parent, text):
    f = Frame(parent, bg=C["card"], padx=10, pady=4)
    f.pack(side=LEFT, padx=(0, 8))
    lbl = Label(f, text=text, font=FONT_SMALL, bg=C["card"], fg=C["muted"])
    lbl.pack()
    return lbl

lbl_total  = stat_chip(stats_inner, "Total: 0")
lbl_shown  = stat_chip(stats_inner, "Shown: 0")
lbl_match  = stat_chip(stats_inner, "Matches: —")

# ── Log Area Header ──────────────────────────────
log_header = Frame(root, bg=C["card"], pady=7)
log_header.pack(fill=X, padx=16)
Frame(log_header, bg=C["border"], height=1).pack(fill=X, side=BOTTOM)
Frame(log_header, bg=C["border"], height=1).pack(fill=X, side=TOP)

log_h_inner = Frame(log_header, bg=C["card"])
log_h_inner.pack(fill=X, padx=10)

Label(log_h_inner, text="LIVE OUTPUT",
      font=FONT_SMALL, bg=C["card"], fg=C["muted"]).pack(side=LEFT)

btn_copy = Button(log_h_inner, text="Copy All", font=FONT_SMALL,
                  bg=C["card"], fg=C["muted"], relief=FLAT, padx=8, pady=2,
                  activebackground=C["border"], cursor="hand2", command=copy_all)
btn_copy.pack(side=RIGHT, padx=(4, 0))

Button(log_h_inner, text="↑ Top", font=FONT_SMALL,
       bg=C["card"], fg=C["muted"], relief=FLAT, padx=8, pady=2,
       activebackground=C["border"], cursor="hand2", command=scroll_top).pack(side=RIGHT, padx=(4, 0))

Button(log_h_inner, text="↓ Bottom", font=FONT_SMALL,
       bg=C["card"], fg=C["muted"], relief=FLAT, padx=8, pady=2,
       activebackground=C["border"], cursor="hand2", command=scroll_bottom).pack(side=RIGHT)

# ── Text Box ──────────────────────────────────────
text_frame = Frame(root, bg=C["bg"])
text_frame.pack(fill=BOTH, expand=True, padx=16, pady=(0, 0))

scrollbar = Scrollbar(text_frame, bg=C["card"], troughcolor=C["surface"],
                      activebackground=C["muted"], width=10)
scrollbar.pack(side=RIGHT, fill=Y)

text_box = Text(text_frame,
                font=FONT_MONO,
                bg=C["surface"],
                fg=C["text"],
                insertbackground=C["accent"],
                selectbackground=C["accent"],
                selectforeground="#000",
                relief=FLAT,
                wrap=WORD,
                state=DISABLED,
                yscrollcommand=scrollbar.set,
                padx=10, pady=8,
                spacing1=2, spacing3=2)
text_box.pack(fill=BOTH, expand=True)
scrollbar.config(command=text_box.yview)

# Text tags
text_box.tag_configure("timestamp", foreground=C["muted"], font=FONT_SMALL)
text_box.tag_configure("message", foreground=C["text"], font=FONT_MONO)
text_box.tag_configure("highlight",
                       background=C["highlight_bg"],
                       foreground=C["highlight_fg"],
                       font=FONT_MONO_B)
text_box.tag_configure("muted", foreground=C["muted"], font=FONT_MONO)

# ── Footer ───────────────────────────────────────
footer = Frame(root, bg=C["card"], pady=6)
footer.pack(fill=X, padx=0)
Frame(footer, bg=C["border"], height=1).pack(fill=X, side=TOP)

foot_inner = Frame(footer, bg=C["card"])
foot_inner.pack(fill=X, padx=16)

btn_autoscroll = Button(foot_inner, text="Auto-scroll: ON",
                        font=FONT_SMALL, bg=C["card"], fg=C["green"],
                        relief=FLAT, padx=0, pady=0,
                        activebackground=C["card"],
                        cursor="hand2", command=toggle_autoscroll)
btn_autoscroll.pack(side=LEFT)

Label(foot_inner, text="LiveFeed Monitor v2.0  ·  PC#1 → PC#2",
      font=FONT_SMALL, bg=C["card"], fg=C["muted"]).pack(side=RIGHT)

# ──────────────────────────────────────────────
# INITIAL PLACEHOLDER
# ──────────────────────────────────────────────
text_box.config(state=NORMAL)
text_box.insert(END, "\n\n   Connecting to server...\n   Waiting for messages.\n\n", "muted")
text_box.config(state=DISABLED)

# ──────────────────────────────────────────────
# START
# ──────────────────────────────────────────────
t = threading.Thread(target=fetch_loop, daemon=True)
t.start()

pulse_dot()

def on_close():
    global fetch_thread_running
    fetch_thread_running = False
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
