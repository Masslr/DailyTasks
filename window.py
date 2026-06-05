import os
import subprocess
from datetime import date, timedelta

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QIcon

from data import load_data, save_data, maybe_reset_daily, add_xp, xp_for_level, DATA_PATH
from widgets import TaskRow, AddRow
from level_widget import LevelPanel

WINDOW_WIDTH = 320
SOUND_PATH = os.path.expanduser("~/ArchMods/tasks_tray/sounds/divine_raw.wav")

def make_icon():
    px = QPixmap(64, 64)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("white"))
    for y in [16, 32, 48]:
        p.drawRoundedRect(8, y - 6, 12, 12, 2, 2)
        p.drawRoundedRect(28, y - 3, 28, 6, 2, 2)
    p.end()
    return QIcon(px)


class TasksWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(WINDOW_WIDTH)
        self.data = {}
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QFrame#card { background: #1f2937; border: 1px solid #374151; border-radius: 12px; }
        """)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Level panel ───────────────────────────────────────────────────────
        self.level_panel = LevelPanel()
        close_btn = QPushButton("X")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.hide)
        close_btn.setStyleSheet("""
            QPushButton { background: transparent; border: 1px solid #4b5563; border-radius: 6px; color: #4b5563; font-size: 12px; font-weight: bold; padding: 0; }
            QPushButton:hover { color: #e5e7eb; border-color: #e5e7eb; }
        """)
        self.level_panel.streak_row_layout.addWidget(close_btn)
        layout.addWidget(self.level_panel)
        layout.addWidget(self._divider())

        # ── Daily section ─────────────────────────────────────────────────────
        daily_container = QWidget()
        daily_layout = QVBoxLayout(daily_container)
        daily_layout.setContentsMargins(0, 8, 0, 4)
        daily_layout.setSpacing(0)

        daily_header = QWidget()
        dhl = QHBoxLayout(daily_header)
        dhl.setContentsMargins(12, 0, 12, 4)
        dhl.addWidget(self._section_label("DAILY"))
        dhl.addStretch()
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #4b5563; font-size: 10px;")
        dhl.addWidget(self.progress_label)
        daily_layout.addWidget(daily_header)

        self.daily_items_layout = QVBoxLayout()
        self.daily_items_layout.setSpacing(0)
        daily_layout.addLayout(self.daily_items_layout)
        daily_layout.addWidget(AddRow("Add daily task…", lambda t: self._add("daily", t)))

        reset_row = QWidget()
        rrl = QHBoxLayout(reset_row)
        rrl.setContentsMargins(12, 2, 12, 8)
        reset_btn = QPushButton("↺  Reset daily")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._reset_daily)
        reset_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #4b5563; font-size: 11px; text-align: left; padding: 0; }
            QPushButton:hover { color: #9ca3af; }
        """)
        rrl.addWidget(reset_btn)
        rrl.addStretch()
        daily_layout.addWidget(reset_row)

        layout.addWidget(daily_container)
        layout.addWidget(self._divider())

        # ── Life section ──────────────────────────────────────────────────────
        life_container = QWidget()
        life_layout = QVBoxLayout(life_container)
        life_layout.setContentsMargins(0, 8, 0, 12)
        life_layout.setSpacing(0)

        life_header = QWidget()
        lhl = QHBoxLayout(life_header)
        lhl.setContentsMargins(12, 0, 12, 4)
        self.life_label = QLabel("Life Goals")
        self.life_label.setStyleSheet("color: #9ca3af; font-size: 13px; font-weight: bold;")
        lhl.addWidget(self.life_label)
        life_layout.addWidget(life_header)

        self.life_items_layout = QVBoxLayout()
        self.life_items_layout.setSpacing(0)
        life_layout.addLayout(self.life_items_layout)
        life_layout.addWidget(AddRow("Add life task…", lambda t: self._add("life", t)))

        layout.addWidget(life_container)

        layout.addWidget(self._divider())

        footer = QWidget()
        footer.setFixedHeight(24)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(12, 1, 12, 1)
        edit_btn = QPushButton("Edit JSON")
        edit_btn.clicked.connect(lambda: subprocess.Popen(["kate", DATA_PATH]))
        edit_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #4b5563; font-size: 13px; padding: 0; }
            QPushButton:hover { color: #e5e7eb; }
        """)
        fl.addStretch()
        fl.addWidget(edit_btn)
        fl.addStretch()
        layout.addWidget(footer)

        outer.addWidget(self.card)

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background: #374151; max-height: 1px; border: none;")
        return line

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #4b5563; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        return lbl

    def refresh(self):
        self.data = load_data()
        maybe_reset_daily(self.data)
        self._render_items()

    def _render_items(self):
        self._clear_layout(self.daily_items_layout)
        self._clear_layout(self.life_items_layout)

        for i, item in enumerate(self.data["daily"]):
            self.daily_items_layout.addWidget(TaskRow(
                item["text"], item["done"],
                on_toggle=lambda i=i: self._toggle("daily", i),
                on_remove=lambda i=i: self._remove("daily", i),
            ))

        for i, item in enumerate(self.data["life"]):
            self.life_items_layout.addWidget(TaskRow(
                item["text"], item["done"],
                on_toggle=lambda i=i: self._toggle("life", i),
                on_remove=lambda i=i: self._remove("life", i),
            ))

        done  = sum(1 for item in self.data["daily"] if item["done"])
        total = len(self.data["daily"])
        self.progress_label.setText(f"{done}/{total}")

        level  = self.data.get("level", 1)
        xp     = self.data.get("experience", 0)
        needed = xp_for_level(level)
        streak = self.data.get("streak", 0)
        self.level_panel.update_stats(level, xp, needed, streak)

        life_goals = self.data.get("life_goals", 0)
        life_str = f"Life Goals  🔥 {life_goals}" if life_goals > 0 else "Life Goals"
        self.life_label.setText(life_str)

        self.card.adjustSize()
        self.adjustSize()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _toggle(self, section, idx):
        self.data[section][idx]["done"] = not self.data[section][idx]["done"]
        if section == "daily":
            self._check_streak()
        if section == "life" and self.data[section][idx]["done"]:
            self.data["life_goals"] = self.data.get("life_goals", 0) + 1
        save_data(self.data)
        self._render_items()

    def _check_streak(self):
        from data import check_streak
        check_streak(self.data)

    def _remove(self, section, idx):
        self.data[section].pop(idx)
        save_data(self.data)
        self._render_items()

    def _add(self, section, text):
        text = text.strip()
        if text:
            self.data[section].append({"text": text, "done": False})
            save_data(self.data)
            self._render_items()

    def _reset_daily(self):
        for item in self.data["daily"]:
            item["done"] = False
        self.data["last_reset"] = str(date.today())
        save_data(self.data)
        self._render_items()

    def show_near_tray(self, tray_geometry):
        self.refresh()
        self.adjustSize()

        self.show()
        self.raise_()
        self.activateWindow()
