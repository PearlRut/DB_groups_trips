# screens/main_menu_screen.py

import tkinter as tk
from ui_helpers import (
    BG_COLOR,
    BLUE,
    GRAY,
    create_title,
    create_subtitle,
    create_button
)


class MainMenuScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app

    def show(self):
        self.app.clear_screen()

        create_title(self.root, "מערכת לניהול טיולים וקבוצות")
        create_subtitle(self.root, "Mini Database Project - Phase E")

        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(pady=12)

        buttons = [
            ("ניהול טיולים", self.app.show_trips_screen),
            ("ניהול משתתפים", self.app.show_participants_screen),
            ("שיבוץ משתתפים לטיולים", self.app.show_trip_assignments_screen),
            ("ניהול משאבי טיול", self.app.show_trip_resources_screen),
            ("ניהול מדריכים", self.app.show_guides_screen),
            ("ניהול מסלולים", lambda: self.app.show_simple_crud_screen("routes")),
            ("ניהול סוגי תחבורה", lambda: self.app.show_simple_crud_screen("transport_types")),
            ("ניהול ספקים", lambda: self.app.show_simple_crud_screen("supplier")),
            ("ניהול מיקומים", lambda: self.app.show_simple_crud_screen("location")),
            ("ניהול ציוד", self.app.show_equipment_screen),
            ("ניהול תחבורה", self.app.show_transportation_screen),
            ("ניהול אירועים ולו״ז", self.app.show_events_schedule_screen),
            ("לוגים ומעקב שינויים", self.app.show_logs_screen),
            ("דוחות, שאילתות ותתי־תוכניות", self.app.show_reports_screen),
            ("יציאה", self.root.quit),
        ]

        for index, (text, command) in enumerate(buttons):
            color = GRAY if text == "יציאה" else BLUE

            btn = create_button(frame, text, command, color=color, width=30)
            btn.grid(
                row=index // 2,
                column=index % 2,
                padx=15,
                pady=6
            )