# screens/logs_screen.py

import tkinter as tk
from tkinter import ttk, messagebox

from db import fetch_all
from ui_helpers import (
    BG_COLOR,
    BLUE,
    GRAY,
    create_title,
    create_button
)


class LogsScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        self.tree_container = None
        self.current_log_type = None

    def show(self):
        self.app.clear_screen()

        create_title(self.root, "לוגים ומעקב שינויים")

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_actions(main_frame)
        self.create_table_area(main_frame)
        self.create_bottom_buttons()

    def create_actions(self, parent):
        actions_frame = tk.LabelFrame(
            parent,
            text="בחרי לוג להצגה",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=15,
            pady=15
        )
        actions_frame.pack(fill="x", pady=10)

        btn1 = create_button(
            actions_frame,
            "לוג שינוי סטטוס טיולים",
            self.show_trip_status_log,
            color=BLUE,
            width=25
        )
        btn1.grid(row=0, column=0, padx=8, pady=8)

        btn2 = create_button(
            actions_frame,
            "לוג שינוי מלאי ציוד",
            self.show_equipment_stock_log,
            color=BLUE,
            width=25
        )
        btn2.grid(row=0, column=1, padx=8, pady=8)

    def create_table_area(self, parent):
        self.tree_container = tk.Frame(parent, bg=BG_COLOR)
        self.tree_container.pack(fill="both", expand=True, pady=10)

        info = tk.Label(
            self.tree_container,
            text="בחרי לוג להצגה",
            font=("Arial", 14),
            bg=BG_COLOR,
            fg="#4b5563"
        )
        info.pack(pady=40)

    def create_bottom_buttons(self):
        bottom_frame = tk.Frame(self.root, bg=BG_COLOR)
        bottom_frame.pack(pady=10)

        back_btn = create_button(
            bottom_frame,
            "חזרה למסך הראשי",
            self.app.show_main_screen,
            color=GRAY,
            width=20
        )
        back_btn.pack(side="left", padx=10)

        refresh_btn = create_button(
            bottom_frame,
            "רענון",
            self.refresh_current_log,
            color=BLUE,
            width=15
        )
        refresh_btn.pack(side="left", padx=10)

    def clear_table_area(self):
        for widget in self.tree_container.winfo_children():
            widget.destroy()

    def display_rows(self, rows):
        self.clear_table_area()

        if not rows:
            messagebox.showinfo("מידע", "לא נמצאו רשומות לוג להצגה")
            return

        columns = list(rows[0].keys())

        tree = ttk.Treeview(self.tree_container, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=160, anchor="center")

        scrollbar_y = ttk.Scrollbar(self.tree_container, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(self.tree_container, orient="horizontal", command=tree.xview)

        tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        self.tree_container.grid_rowconfigure(0, weight=1)
        self.tree_container.grid_columnconfigure(0, weight=1)

        for row in rows:
            tree.insert(
                "",
                "end",
                values=[
                    "" if row[col] is None else row[col]
                    for col in columns
                ]
            )

    def show_trip_status_log(self):
        self.current_log_type = "trip_status"

        # שאילתת SELECT לשליפת לוג שינויי הסטטוס של הטיולים.
        # טבלה זו (trip_status_log) מתעדכנת אוטומטית על ידי טריגר בבסיס הנתונים (Database Trigger) 
        # בכל פעם שמתבצע שינוי בעמודת הסטטוס של טבלת הטיולים.
        # אנו מבצעים LEFT JOIN לטבלת הטיולים כדי להציג את שם הטיול הנוכחי.
        query = """
            SELECT
                l.log_id,
                l.trip_id,
                t.trip_name,
                l.old_status,
                l.new_status,
                l.changed_at,
                l.changed_by
            FROM public.trip_status_log l
            LEFT JOIN public.trips t
                ON l.trip_id = t.trip_id
            ORDER BY l.changed_at DESC, l.log_id DESC;
        """

        rows = fetch_all(query)
        self.display_rows(rows)

    def show_equipment_stock_log(self):
        self.current_log_type = "equipment_stock"

        # שאילתת SELECT לשליפת לוג שינויי המלאי של הציוד.
        # גם טבלה זו (equipment_stock_log) מוזנת באמצעות טריגר ייעודי השומר היסטוריית שינויים,
        # ומציגה את הכמות הישנה, החדשה, ואת ההפרש שנוצר (quantity_changed).
        query = """
            SELECT
                l.log_id,
                l.equipmentid,
                e.itemname AS equipment_name,
                l.old_totalinstock,
                l.new_totalinstock,
                l.quantity_changed,
                l.changed_at,
                l.changed_by
            FROM public.equipment_stock_log l
            LEFT JOIN public.equipment e
                ON l.equipmentid = e.equipmentid
            ORDER BY l.changed_at DESC, l.log_id DESC;
        """

        rows = fetch_all(query)
        self.display_rows(rows)

    def refresh_current_log(self):
        if self.current_log_type == "trip_status":
            self.show_trip_status_log()
        elif self.current_log_type == "equipment_stock":
            self.show_equipment_stock_log()
        else:
            messagebox.showinfo("מידע", "בחרי קודם איזה לוג להציג")