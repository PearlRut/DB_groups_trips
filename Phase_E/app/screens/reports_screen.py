# screens/reports_screen.py

import tkinter as tk
from tkinter import ttk, messagebox

from db import fetch_all, execute_query
from ui_helpers import (
    BG_COLOR,
    BLUE,
    GREEN,
    ORANGE,
    GRAY,
    create_title,
    create_button
)


class ReportsScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.tree = None
        self.trip_id_var = tk.StringVar()

    def show(self):
        self.app.clear_screen()

        create_title(self.root, "דוחות, שאילתות ותתי־תוכניות")

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_actions(main_frame)
        self.create_table_area(main_frame)
        self.create_bottom_buttons()

    def create_actions(self, parent):
        actions_frame = tk.LabelFrame(
            parent,
            text="פעולות",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=15,
            pady=15
        )
        actions_frame.pack(fill="x", pady=10)

        btn1 = create_button(
            actions_frame,
            "דוח תכנון טיולים",
            self.show_trip_planning_summary,
            color=BLUE,
            width=22
        )
        btn1.grid(row=0, column=0, padx=8, pady=8)

        btn2 = create_button(
            actions_frame,
            "דוח לוגיסטיקה ותפעול",
            self.show_trip_logistics_operations,
            color=BLUE,
            width=22
        )
        btn2.grid(row=0, column=1, padx=8, pady=8)

        trip_id_label = tk.Label(
            actions_frame,
            text="Trip ID:",
            font=("Arial", 11),
            bg=BG_COLOR
        )
        trip_id_label.grid(row=1, column=0, padx=8, pady=8, sticky="e")

        trip_id_entry = tk.Entry(
            actions_frame,
            textvariable=self.trip_id_var,
            width=15,
            font=("Arial", 11)
        )
        trip_id_entry.grid(row=1, column=1, padx=8, pady=8, sticky="w")

        btn3 = create_button(
            actions_frame,
            "סיכום תפוסה לטיול",
            self.run_trip_occupancy_function,
            color=GREEN,
            width=22
        )
        btn3.grid(row=1, column=2, padx=8, pady=8)

        btn4 = create_button(
            actions_frame,
            "עדכון סטטוס לפי תפוסה",
            self.run_update_trip_status_procedure,
            color=ORANGE,
            width=24
        )
        btn4.grid(row=0, column=2, padx=8, pady=8)

    def create_table_area(self, parent):
        table_frame = tk.Frame(parent, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, pady=10)

        self.tree_container = table_frame

        info = tk.Label(
            table_frame,
            text="בחרי דוח או פעולה להצגה",
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

    def clear_table_area(self):
        for widget in self.tree_container.winfo_children():
            widget.destroy()

    def display_rows(self, rows):
        self.clear_table_area()

        if not rows:
            messagebox.showinfo("מידע", "לא נמצאו נתונים להצגה")
            return

        columns = list(rows[0].keys())

        tree = ttk.Treeview(self.tree_container, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")

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

        self.tree = tree

    def show_trip_planning_summary(self):
        query = """
            SELECT *
            FROM public.trip_planning_summary_view
            ORDER BY trip_id;
        """

        rows = fetch_all(query)
        self.display_rows(rows)

    def show_trip_logistics_operations(self):
        query = """
            SELECT *
            FROM public.trip_logistics_operations_view
            ORDER BY trip_id;
        """

        rows = fetch_all(query)
        self.display_rows(rows)

    def run_trip_occupancy_function(self):
        trip_id = self.trip_id_var.get().strip()

        if not trip_id:
            messagebox.showwarning("שגיאה", "יש להזין Trip ID")
            return

        query = """
            SELECT *
            FROM public.get_trip_occupancy_summary(%s);
        """

        rows = fetch_all(query, (trip_id,))
        self.display_rows(rows)

    def run_update_trip_status_procedure(self):
        confirm = messagebox.askyesno(
            "אישור פעולה",
            "האם להפעיל את הפרוצדורה שמעדכנת סטטוסי טיולים לפי תפוסה?"
        )

        if not confirm:
            return

        query = """
            CALL public.update_trip_status_by_occupancy();
        """

        success, message = execute_query(query)

        if success:
            messagebox.showinfo(
                "הצלחה",
                "הפרוצדורה הופעלה בהצלחה. ניתן לבדוק את השינוי בדוח תכנון טיולים או במסך ניהול טיולים."
            )
            self.show_trip_planning_summary()
        else:
            messagebox.showerror("שגיאה", message)