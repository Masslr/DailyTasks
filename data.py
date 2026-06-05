import json
import subprocess
import os
from datetime import date, timedelta

DATA_PATH = os.path.expanduser("~/.local/share/tasks_tray/tasks.json")

SOUND_STREAK   = os.path.expanduser("~/ArchMods/tasks_tray/sounds/divine_quiet.wav")
SOUND_LEVEL_UP = os.path.expanduser("~/ArchMods/tasks_tray/sounds/levelup.wav")

# ── Level / XP config — tweak these freely ───────────────────────────────────
XP_PER_STREAK       = 50    # XP gained when daily streak increments
XP_LOSS_ON_RESET    = 30    # XP lost when streak breaks
XP_BASE             = 100   # XP needed for level 1 → 2
XP_GROWTH           = 1.4   # each level needs XP_BASE * (XP_GROWTH ^ level) more XP
# -----------------------------------------------------------------------------

DEFAULT_DATA = {
    "last_reset": "",
    "streak": 0,
    "life_goals": 0,
    "level": 1,
    "experience": 0,
    "last_completed": "",
    "daily": [
        {"text": "Take vitamins", "done": False},
        {"text": "Exercise", "done": False},
        {"text": "Check messages", "done": False},
    ],
    "life": [
        {"text": "Book dentist appointment", "done": False},
    ]
}

def xp_for_level(level: int) -> int:
    """XP required to go from `level` to `level + 1`."""
    return int(XP_BASE * (XP_GROWTH ** (level - 1)))

def load_data():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA
    with open(DATA_PATH) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def add_xp(data, amount: int):
    """Add XP, handling level-ups. Returns True if a level-up occurred."""
    data["experience"] = data.get("experience", 0) + amount
    leveled_up = False
    while True:
        needed = xp_for_level(data["level"])
        if data["experience"] >= needed:
            data["experience"] -= needed
            data["level"] += 1
            leveled_up = True
        else:
            break
    return leveled_up

def remove_xp(data, amount: int):
    """Remove XP, floor at 0, no de-levelling."""
    data["experience"] = max(0, data.get("experience", 0) - amount)

def maybe_reset_daily(data):
    today = str(date.today())
    if data.get("last_reset") != today:
        yesterday = str(date.today() - timedelta(days=1))
        last_completed = data.get("last_completed", "")
        # streak broke — lose XP
        if last_completed != yesterday and last_completed != today:
            if data.get("streak", 0) > 0:
                remove_xp(data, XP_LOSS_ON_RESET)
            data["streak"] = 0
        for item in data["daily"]:
            item["done"] = False
        data["daily"] = [i for i in data["daily"] if not i.get("scheduled")]
        day_name = date.today().strftime("%A")
        for text in data.get("daily_schedule", {}).get(day_name, []):
            data["daily"].append({"text": text, "done": False, "scheduled": True})
        data["last_reset"] = today
        save_data(data)

def check_streak(data) -> bool:
    """Returns True if a level-up occurred."""
    if not all(item["done"] for item in data["daily"]):
        return False
    today     = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    last      = data.get("last_completed", "")
    if last == today:
        return False  # already counted today
    if last == yesterday:
        data["streak"] = data.get("streak", 0) + 1
    else:
        data["streak"] = 1
    data["last_completed"] = today
    leveled_up = add_xp(data, XP_PER_STREAK)
    if leveled_up:
        subprocess.Popen(["paplay", SOUND_LEVEL_UP])
    else:
        subprocess.Popen(["paplay", SOUND_STREAK])
    return leveled_up
