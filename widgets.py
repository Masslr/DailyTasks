from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt

class TaskRow(QWidget):
    def __init__(self, text, done, on_toggle, on_remove):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 8, 4)
        layout.setSpacing(8)

        self.check_btn = QPushButton()
        self.check_btn.setFixedSize(18, 18)
        self.check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_btn.clicked.connect(lambda _: on_toggle())

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.label.mousePressEvent = lambda e: on_toggle()

        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(15, 15)
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_btn.clicked.connect(lambda _: on_remove())
        self.remove_btn.setVisible(False)
        self.remove_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #6b7280; font-size: 16px; }
            QPushButton:hover { color: #ef4444; }
        """)

        layout.addWidget(self.check_btn)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.remove_btn)
        self._set_done(done)

    def enterEvent(self, e):
        self.remove_btn.setVisible(True)

    def leaveEvent(self, e):
        self.remove_btn.setVisible(False)

    def _set_done(self, done):
        if done:
            self.check_btn.setStyleSheet("""
                QPushButton {
                    background: #4ade80; border: 1.5px solid #22c55e;
                    border-radius: 9px; font-size: 11px; color: white;
                }
            """)
            self.check_btn.setText("✓")
            self.label.setStyleSheet("color: #6b7280; text-decoration: line-through; font-size: 13px;")
        else:
            self.check_btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: 1.5px solid #4b5563;
                    border-radius: 9px; font-size: 11px; color: transparent;
                }
                QPushButton:hover { border-color: #9ca3af; }
            """)
            self.check_btn.setText("")
            self.label.setStyleSheet("color: #e5e7eb; font-size: 13px;")


class AddRow(QWidget):
    def __init__(self, placeholder, on_add):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(6)

        plus = QLabel("+")
        plus.setStyleSheet("color: #4b5563; font-size: 16px;")
        plus.setFixedWidth(14)

        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet("""
            QLineEdit { background: transparent; border: none; color: #9ca3af; font-size: 13px; padding: 2px 0; }
            QLineEdit:focus { color: #e5e7eb; }
        """)
        inp.returnPressed.connect(lambda: (on_add(inp.text()), inp.clear()))

        layout.addWidget(plus)
        layout.addWidget(inp, 1)
