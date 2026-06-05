from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush, QImage
import os

# ── Colours — tweak freely ────────────────────────────────────────────────────
BADGE_BG        = QColor("#1e3a5f")   # level badge background
BADGE_BORDER    = QColor("#3b82f6")   # level badge ring
BADGE_TEXT      = QColor("#93c5fd")   # level number colour
BAR_BG          = QColor("#374151")   # XP bar background
BAR_FILL        = QColor("#3b82f6")   # XP bar fill
BAR_TEXT        = QColor("#6b7280")   # XP numbers
# -----------------------------------------------------------------------------

BADGE_IMAGE_PATH = os.path.expanduser("~/ArchMods/tasks_tray/icons/level_badge_4.png")

class LevelBadge(QWidget):
    SIZE = 60

    def __init__(self):
        super().__init__()
        self.setFixedSize(self.SIZE, self.SIZE)
        self._level = 1
        self._bg = QPixmap(BADGE_IMAGE_PATH).scaled(
            self.SIZE, self.SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    def set_level(self, level: int):
        self._level = level
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.drawPixmap(0, 0, self._bg)
        p.setPen(QColor("white"))
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        p.setFont(font)
        p.drawText(QRect(0, 0, self.SIZE, self.SIZE), Qt.AlignmentFlag.AlignCenter, str(self._level))
        p.end()

class XpBar(QWidget):
    """Thin XP progress bar with current/needed text."""
    HEIGHT = 6

    def __init__(self):
        super().__init__()
        self.setFixedHeight(self.HEIGHT + 18)  # bar + text row
        self._xp = 0
        self._needed = 100

    def set_xp(self, xp: int, needed: int):
        self._xp = xp
        self._needed = needed
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()

        # XP text
        p.setPen(BAR_TEXT)
        font = QFont()
        font.setPixelSize(10)
        p.setFont(font)
        p.drawText(QRect(0, 0, w, 14), Qt.AlignmentFlag.AlignRight, f"{self._xp} / {self._needed} XP")

        # bar background
        bar_y = 16
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(BAR_BG)
        p.drawRoundedRect(0, bar_y, w, self.HEIGHT, 3, 3)

        # bar fill
        fill_w = int(w * min(self._xp / max(self._needed, 1), 1.0))
        if fill_w > 0:
            p.setBrush(BAR_FILL)
            p.drawRoundedRect(0, bar_y, fill_w, self.HEIGHT, 3, 3)

        p.end()


class LevelPanel(QWidget):
    """Badge + streak label + XP bar combined into one panel."""
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setContentsMargins(16, 1, 12, 1)
        layout.setSpacing(10)

        self.badge = LevelBadge()
        layout.addWidget(self.badge)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)

        streak_row = QWidget()
        srl = QHBoxLayout(streak_row)
        srl.setContentsMargins(0, 0, 0, 0)
        self.streak_label = QLabel("Daily Streak  0")
        self.streak_label.setStyleSheet("color: #9ca3af; font-size: 13px; font-weight: bold;")
        srl.addWidget(self.streak_label)
        srl.addStretch()
        self.streak_row_layout = srl
        rl.addWidget(streak_row)

        self.xp_bar = XpBar()
        rl.addWidget(self.xp_bar)

        layout.addWidget(right, 1)

    def update_stats(self, level: int, xp: int, needed: int, streak: int):
        self.badge.set_level(level)
        streak_str = f"Daily Streak  🔥 {streak}" if streak > 0 else "Daily Streak  0"
        self.streak_label.setText(streak_str)
        self.xp_bar.set_xp(xp, needed)
