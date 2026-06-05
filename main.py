#!/usr/bin/env python3
import sys
import subprocess
from datetime import date, datetime

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction

# add the tasks_tray folder to path so sibling imports work
import os
sys.path.insert(0, os.path.dirname(__file__))

from data import load_data
from window import TasksWindow, make_icon

def main():
    QApplication.setApplicationName("tasks-tray")
    QApplication.setDesktopFileName("tasks-tray")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = TasksWindow()
    tray = QSystemTrayIcon(make_icon(), app)
    tray.setToolTip("Tasks")

    menu = QMenu()
    quit_action = QAction("Quit", app)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)

    def on_tray_click(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if window.isVisible():
                window.hide()
            else:
                window.show_near_tray(tray.geometry())

    tray.activated.connect(on_tray_click)
    tray.show()
    QTimer.singleShot(1500, lambda: window.show_near_tray(tray.geometry()))

    # 8pm reminder for undone daily tasks
    notification_sent_date = {"date": None}

    def check_evening_notification():
        now = datetime.now()
        today = str(date.today())
        if now.hour == 20 and notification_sent_date["date"] != today:
            data = load_data()
            undone = [i["text"] for i in data["daily"] if not i["done"]]
            if undone:
                notification_sent_date["date"] = today
                subprocess.Popen([
                    "notify-send", "--app-name=Tasks", "--urgency=normal",
                    f"📋 {len(undone)} daily task{'s' if len(undone) > 1 else ''} still to do",
                    "\n".join(f"• {t}" for t in undone)
                ])

    notify_timer = QTimer()
    notify_timer.timeout.connect(check_evening_notification)
    notify_timer.start(60_000)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
