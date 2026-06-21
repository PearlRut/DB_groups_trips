# screens/main_menu_screen.py
# מסך התפריט הראשי - מאפשר ניווט לכלל הישויות והדוחות במערכת

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
        self.root = root # content_frame שמגיע מה-AppController
        self.app = app   # ה-AppController עצמו לצורך ניווט ומעברי מסכים

    def show(self):
        # ניקוי כל רכיבי המסך הקודם
        self.app.clear_screen()

        # כותרות מעוצבות לתפריט הראשי
        create_title(self.root, "מערכת לניהול טיולים וקבוצות")
        create_subtitle(self.root, "Mini Database Project - Phase E")

        # פאנל שיאגד את כפתורי הניווט
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(pady=12)

        # רשימת כפתורים: כל כפתור מוגדר על ידי טקסט (כותרת הכפתור) ופונקציית הקריאה החוזרת (callback) שלו.
        # שימוש ב-lambda מבוצע כאשר אנו צריכים להעביר ארגומנט (כמו מפתח הטבלה למסך ה-CRUD הגנרי).
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
            ("יציאה", self.root.quit), # quit סוגר את האפליקציה לחלוטין
        ]

        # יצירה וסידור אוטומטי של הכפתורים ברשת (Grid) של 2 עמודות
        for index, (text, command) in enumerate(buttons):
            color = GRAY if text == "יציאה" else BLUE

            btn = create_button(frame, text, command, color=color, width=30)
            btn.grid(
                row=index // 2,     # שורה: חילוק שלם ב-2 (למשל: אינדקסים 0 ו-1 יהיו בשורה 0, 2 ו-3 בשורה 1 וכד')
                column=index % 2,   # עמודה: שארית חילוק ב-2 (אינדקס זוגי משמאל, אינדקס אי-זוגי מימין)
                padx=15,
                pady=6
            )