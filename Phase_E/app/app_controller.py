# app_controller.py
# קובץ ה-Controller המרכזי של האפליקציה - מנהל את החלון הראשי, הניווט ומעבר בין המסכים השונים

import tkinter as tk
from screens.main_menu_screen import MainMenuScreen
from screens.trips_screen import TripsScreen
from screens.participants_screen import ParticipantsScreen
from screens.simple_crud_screen import SimpleCrudScreen
from screens.reports_screen import ReportsScreen
from screens.equipment_screen import EquipmentScreen
from screens.transportation_screen import TransportationScreen
from screens.guides_screen import GuidesScreen
from screens.logs_screen import LogsScreen
from screens.events_schedule_screen import EventsScheduleScreen
from screens.trip_assignments_screen import TripAssignmentsScreen
from screens.trip_resources_screen import TripResourcesScreen


class AppController:
    def __init__(self, root):
        self.root = root
        self.root.title("Trip Management System - Stage E")
        self.root.geometry("1250x780") # הגדרת גודל ראשוני קבוע לחלון
        self.root.configure(bg="#f4f6f8")

        # יצירת frame ראשי המכיל את כל תוכן המסכים.
        # ניקוי ה-frame הזה מאפשר לעבור בין מסכים שונים ללא יצירת חלונות חדשים ומניעת כפילויות/שאריות גרפיות ב-macOS.
        self.content_frame = tk.Frame(self.root, bg="#f4f6f8")
        self.content_frame.pack(fill="both", expand=True)

        # הגדרת תצורה (Configuration) לטבלאות פשוטות.
        # מנגנון זה מאפשר להשתמש במסך CRUD גנרי יחיד (SimpleCrudScreen) עבור מספר טבלאות דומות,
        # על ידי הגדרת העמודות, מפתחות ראשיים, סוגי פקדים ואפשרויות הבחירה לכל טבלה.
        self.simple_tables = {
            "routes": {
                "title": "ניהול מסלולים",
                "table_name": "routes",
                "primary_key": "route_id",
                "fields": [
                    ("route_id", "Route ID", True, "text", None),
                    ("route_name", "Route Name", True, "text", None),
                    ("region", "Region", True, "combo", ["North", "South", "Center", "Jerusalem", "East", "West"]),
                    ("distance_km", "Distance KM", True, "text", None),
                    ("duration_hours", "Duration Hours", True, "text", None),
                    ("difficulty_level", "Difficulty Level", True, "combo", ["Easy", "Medium", "Hard"]),
                ],
            },
            "transport_types": {
                "title": "ניהול סוגי תחבורה",
                "table_name": "transport_types",
                "primary_key": "transport_type_id",
                "fields": [
                    ("transport_type_id", "Transport Type ID", True, "text", None),
                    ("transport_type_name", "Transport Type Name", True, "text", None),
                ],
            },
            "supplier": {
                "title": "ניהול ספקים",
                "table_name": "supplier",
                "primary_key": "supplierid",
                "fields": [
                    ("supplierid", "Supplier ID", True, "text", None),
                    ("company_name", "Company Name", True, "text", None),
                    ("service_type", "Service Type", True, "combo_editable", ["Food", "Bus", "Gear", "Guide", "Medical", "Security", "Other"]),
                    ("contactphone", "Contact Phone", True, "text", None),
                ],
            },
            "location": {
                "title": "ניהול מיקומים",
                "table_name": "location",
                "primary_key": "locationid",
                "fields": [
                    ("locationid", "Location ID", True, "text", None),
                    ("locationname", "Location Name", True, "text", None),
                    ("region", "Region", True, "combo", ["North", "South", "Center", "Jerusalem", "East", "West"]),
                    ("address", "Address", True, "text", None),
                    ("description", "Description", False, "text", None),
                ],
            },
        }

        # הצגת מסך התפריט הראשי עם עליית התוכנית
        self.show_main_screen()

    def clear_screen(self):
        """
        פונקציה המנקה את כל הרכיבים (widgets) מתוך ה-content_frame הראשי.
        נקראת תמיד רגע לפני טעינת מסך חדש כדי למנוע "שאריות" של רכיבים מהמסך הקודם.
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.root.update_idletasks() # כופה על מערכת הגרפיקה לבצע עדכון מיידי של התצוגה

    # פונקציות הניווט השונות:
    # כל פונקציה מנקה את המסך, מאתחלת את מחלקת המסך הרצוי ומציגה אותה.

    def show_main_screen(self):
        screen = MainMenuScreen(self.content_frame, self)
        screen.show()

    def show_trips_screen(self):
        screen = TripsScreen(self.content_frame, self)
        screen.show()

    def show_participants_screen(self):
        screen = ParticipantsScreen(self.content_frame, self)
        screen.show()

    def show_trip_assignments_screen(self):
        screen = TripAssignmentsScreen(self.content_frame, self)
        screen.show()

    def show_trip_resources_screen(self):
        screen = TripResourcesScreen(self.content_frame, self)
        screen.show()

    def show_equipment_screen(self):
        screen = EquipmentScreen(self.content_frame, self)
        screen.show()

    def show_transportation_screen(self):
        screen = TransportationScreen(self.content_frame, self)
        screen.show()

    def show_guides_screen(self):
        screen = GuidesScreen(self.content_frame, self)
        screen.show()

    def show_logs_screen(self):
        screen = LogsScreen(self.content_frame, self)
        screen.show()

    def show_events_schedule_screen(self):
        screen = EventsScheduleScreen(self.content_frame, self)
        screen.show()

    def show_simple_crud_screen(self, table_key):
        """
        מציג מסך CRUD גנרי לפי טבלה שנבחרה (routes, transport_types, supplier, location).
        שולף את ההגדרות מהמילון self.simple_tables ומעביר אותן לבנאי של SimpleCrudScreen.
        """
        config = self.simple_tables[table_key]
        screen = SimpleCrudScreen(self.content_frame, self, config)
        screen.show()

    def show_reports_screen(self):
        screen = ReportsScreen(self.content_frame, self)
        screen.show()