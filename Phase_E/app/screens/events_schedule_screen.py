# screens/events_schedule_screen.py

import tkinter as tk
from tkinter import ttk, messagebox

from db import fetch_all, fetch_one, execute_query
from ui_helpers import (
    BG_COLOR,
    BLUE,
    GREEN,
    ORANGE,
    RED,
    GRAY,
    create_title,
    create_button,
    create_table
)


class EventsScheduleScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        self.trip_label_to_id = {}
        self.event_label_to_id = {}

        self.event_tree = None
        self.action_tree = None
        self.schedule_tree = None

        self.event_trip_combo = None
        self.action_event_combo = None
        self.schedule_trip_combo = None

        self.event_id_var = tk.StringVar()
        self.event_name_var = tk.StringVar()
        self.event_date_var = tk.StringVar()
        self.event_start_hour_var = tk.StringVar()
        self.event_end_hour_var = tk.StringVar()
        self.event_cost_var = tk.StringVar()
        self.event_status_var = tk.StringVar()
        self.event_trip_var = tk.StringVar()
        self.event_order_num_var = tk.StringVar()

        self.action_id_var = tk.StringVar()
        self.action_name_var = tk.StringVar()
        self.action_type_var = tk.StringVar()
        self.action_address_var = tk.StringVar()
        self.action_event_var = tk.StringVar()

        self.schedule_trip_var = tk.StringVar()
        self.schedule_order_num_var = tk.StringVar()
        self.schedule_date_var = tk.StringVar()
        self.schedule_start_time_var = tk.StringVar()
        self.schedule_end_time_var = tk.StringVar()
        self.schedule_description_var = tk.StringVar()

    def show(self):
        self.app.clear_screen()
        create_title(self.root, "ניהול אירועים ולו״ז")

        self.load_reference_data()

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        events_tab = tk.Frame(notebook, bg=BG_COLOR)
        actions_tab = tk.Frame(notebook, bg=BG_COLOR)
        schedules_tab = tk.Frame(notebook, bg=BG_COLOR)

        notebook.add(events_tab, text="אירועים")
        notebook.add(actions_tab, text="פעולות")
        notebook.add(schedules_tab, text="לו״ז")

        self.create_events_tab(events_tab)
        self.create_actions_tab(actions_tab)
        self.create_schedules_tab(schedules_tab)

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
            self.refresh_all,
            color=GREEN,
            width=15
        )
        refresh_btn.pack(side="left", padx=10)

        self.load_events_table()
        self.load_actions_table()
        self.load_schedules_table()

    def load_reference_data(self):
        self.trip_label_to_id = {}
        self.event_label_to_id = {}

        trips = fetch_all("""
            SELECT trip_id, trip_name, start_date
            FROM public.trips
            ORDER BY trip_name;
        """)

        for row in trips:
            label = f"{row['trip_name']} | {row['start_date']}"
            self.trip_label_to_id[label] = row["trip_id"]

        events = fetch_all("""
            SELECT
                e.event_id,
                e.event_name,
                e.event_date,
                t.trip_name
            FROM public.events e
            JOIN public.trips t
                ON e.trip_id = t.trip_id
            ORDER BY e.event_name;
        """)

        for row in events:
            label = f"{row['event_name']} | {row['event_date']} | {row['trip_name']}"
            self.event_label_to_id[label] = row["event_id"]

    def refresh_all(self):
        self.load_reference_data()

        if self.event_trip_combo is not None:
            self.event_trip_combo["values"] = list(self.trip_label_to_id.keys())

        if self.schedule_trip_combo is not None:
            self.schedule_trip_combo["values"] = list(self.trip_label_to_id.keys())

        if self.action_event_combo is not None:
            self.action_event_combo["values"] = list(self.event_label_to_id.keys())

        self.load_events_table()
        self.load_actions_table()
        self.load_schedules_table()

    # ---------------------------------------------------
    # Events tab
    # ---------------------------------------------------
    def create_events_tab(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי אירוע",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=12,
            pady=12
        )
        form_frame.pack(fill="x", padx=10, pady=8)

        fields = [
            ("Event ID", self.event_id_var, "entry", None),
            ("Event Name *", self.event_name_var, "entry", None),
            ("Event Date YYYY-MM-DD *", self.event_date_var, "entry", None),
            ("Start Hour HH:MM *", self.event_start_hour_var, "entry", None),
            ("End Hour HH:MM *", self.event_end_hour_var, "entry", None),
            ("Cost *", self.event_cost_var, "entry", None),
            ("Status *", self.event_status_var, "combo_editable", ["PLANNED", "OPEN", "COMPLETED", "CANCELLED", "Other"]),
            ("Trip *", self.event_trip_var, "combo", list(self.trip_label_to_id.keys())),
            ("Order Number *", self.event_order_num_var, "entry", None),
        ]

        for index, (label_text, var, widget_type, options) in enumerate(fields):
            label = tk.Label(form_frame, text=label_text, font=("Arial", 10), bg=BG_COLOR)
            label.grid(row=index // 3, column=(index % 3) * 2, padx=8, pady=7, sticky="w")

            if widget_type == "combo":
                widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="readonly",
                    width=25,
                    font=("Arial", 10)
                )
                self.event_trip_combo = widget
            elif widget_type == "combo_editable":
                widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="normal",
                    width=25,
                    font=("Arial", 10)
                )
            else:
                widget = tk.Entry(form_frame, textvariable=var, width=27, font=("Arial", 10))

            widget.grid(row=index // 3, column=(index % 3) * 2 + 1, padx=8, pady=7)

        actions_frame = tk.Frame(parent, bg=BG_COLOR)
        actions_frame.pack(fill="x", padx=10, pady=5)

        buttons = [
            ("שליפה לפי ID", self.load_event_by_id, BLUE, 16),
            ("הוספה", self.add_event, GREEN, 12),
            ("עדכון", self.update_event, ORANGE, 12),
            ("מחיקה", self.delete_event, RED, 12),
            ("ניקוי שדות", self.clear_event_form, GRAY, 14),
        ]

        for text, command, color, width in buttons:
            btn = create_button(actions_frame, text, command, color=color, width=width)
            btn.pack(side="left", padx=5)

        table_frame = tk.Frame(parent, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = [
            "event_id",
            "event_name",
            "event_date",
            "start_hour",
            "end_hour",
            "cost",
            "status",
            "trip_name",
            "order_num"
        ]

        headings = {
            "event_id": "Event ID",
            "event_name": "Event Name",
            "event_date": "Date",
            "start_hour": "Start",
            "end_hour": "End",
            "cost": "Cost",
            "status": "Status",
            "trip_name": "Trip",
            "order_num": "Order"
        }

        self.event_tree = create_table(table_frame, columns, headings)
        self.event_tree.bind("<<TreeviewSelect>>", self.on_event_select)

    def load_events_table(self):
        if self.event_tree is None:
            return

        for item in self.event_tree.get_children():
            self.event_tree.delete(item)

        rows = fetch_all("""
            SELECT
                e.event_id,
                e.event_name,
                e.event_date,
                e.start_hour,
                e.end_hour,
                e.cost,
                e.status,
                t.trip_name,
                e.order_num
            FROM public.events e
            JOIN public.trips t
                ON e.trip_id = t.trip_id
            ORDER BY e.event_id;
        """)

        for row in rows:
            self.event_tree.insert(
                "",
                "end",
                values=[
                    row["event_id"],
                    row["event_name"],
                    row["event_date"],
                    row["start_hour"],
                    row["end_hour"],
                    row["cost"],
                    row["status"],
                    row["trip_name"],
                    row["order_num"]
                ]
            )

    def clear_event_form(self):
        self.event_id_var.set("")
        self.event_name_var.set("")
        self.event_date_var.set("")
        self.event_start_hour_var.set("")
        self.event_end_hour_var.set("")
        self.event_cost_var.set("")
        self.event_status_var.set("")
        self.event_trip_var.set("")
        self.event_order_num_var.set("")

    def on_event_select(self, event):
        selected = self.event_tree.selection()
        if not selected:
            return

        values = self.event_tree.item(selected[0], "values")
        self.event_id_var.set(values[0])
        self.event_name_var.set(values[1])
        self.event_date_var.set(values[2])
        self.event_start_hour_var.set(values[3])
        self.event_end_hour_var.set(values[4])
        self.event_cost_var.set(values[5])
        self.event_status_var.set(values[6])
        self.event_order_num_var.set(values[8])

        event_id = values[0]
        row = fetch_one("""
            SELECT t.trip_name, t.start_date
            FROM public.events e
            JOIN public.trips t
                ON e.trip_id = t.trip_id
            WHERE e.event_id = %s;
        """, (event_id,))

        if row:
            self.event_trip_var.set(f"{row['trip_name']} | {row['start_date']}")

    def get_next_event_id(self):
        row = fetch_one("""
            SELECT COALESCE(MAX(event_id), 0) + 1 AS next_id
            FROM public.events;
        """)
        return 1 if row is None else row["next_id"]

    def validate_event_form(self, require_id=False):
        if require_id and not self.event_id_var.get().strip():
            messagebox.showwarning("שגיאה", "יש להזין Event ID")
            return False

        required = [
            (self.event_name_var.get().strip(), "Event Name"),
            (self.event_date_var.get().strip(), "Event Date"),
            (self.event_start_hour_var.get().strip(), "Start Hour"),
            (self.event_end_hour_var.get().strip(), "End Hour"),
            (self.event_cost_var.get().strip(), "Cost"),
            (self.event_status_var.get().strip(), "Status"),
            (self.event_trip_var.get().strip(), "Trip"),
            (self.event_order_num_var.get().strip(), "Order Number"),
        ]

        for value, name in required:
            if value == "":
                messagebox.showwarning("שגיאה", f"יש למלא את השדה: {name}")
                return False

        if self.event_trip_var.get().strip() not in self.trip_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Trip מתוך הרשימה")
            return False

        try:
            float(self.event_cost_var.get().strip())
            int(self.event_order_num_var.get().strip())
        except ValueError:
            messagebox.showwarning("שגיאה", "Cost חייב להיות מספר ו-Order Number חייב להיות מספר שלם")
            return False

        return True

    def add_event(self):
        if not self.validate_event_form(require_id=False):
            return

        event_id = self.event_id_var.get().strip()
        if event_id == "":
            event_id = self.get_next_event_id()

        trip_id = self.trip_label_to_id[self.event_trip_var.get().strip()]

        query = """
            INSERT INTO public.events
                (event_id, event_name, event_date, start_hour, end_hour, cost, status, trip_id, order_num)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        params = (
            event_id,
            self.event_name_var.get().strip(),
            self.event_date_var.get().strip(),
            self.event_start_hour_var.get().strip(),
            self.event_end_hour_var.get().strip(),
            self.event_cost_var.get().strip(),
            self.event_status_var.get().strip(),
            trip_id,
            self.event_order_num_var.get().strip()
        )

        success, message = execute_query(query, params)

        if success:
            messagebox.showinfo("הצלחה", "האירוע נוסף בהצלחה")
            self.clear_event_form()
            self.refresh_all()
        else:
            messagebox.showerror("שגיאה", message)

    def update_event(self):
        if not self.validate_event_form(require_id=True):
            return

        trip_id = self.trip_label_to_id[self.event_trip_var.get().strip()]

        query = """
            UPDATE public.events
            SET
                event_name = %s,
                event_date = %s,
                start_hour = %s,
                end_hour = %s,
                cost = %s,
                status = %s,
                trip_id = %s,
                order_num = %s
            WHERE event_id = %s;
        """

        params = (
            self.event_name_var.get().strip(),
            self.event_date_var.get().strip(),
            self.event_start_hour_var.get().strip(),
            self.event_end_hour_var.get().strip(),
            self.event_cost_var.get().strip(),
            self.event_status_var.get().strip(),
            trip_id,
            self.event_order_num_var.get().strip(),
            self.event_id_var.get().strip()
        )

        success, message = execute_query(query, params)

        if success:
            messagebox.showinfo("הצלחה", "האירוע עודכן בהצלחה")
            self.refresh_all()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_event(self):
        event_id = self.event_id_var.get().strip()

        if not event_id:
            messagebox.showwarning("שגיאה", "יש להזין Event ID למחיקה")
            return

        confirm = messagebox.askyesno(
            "אישור מחיקה",
            "האם למחוק את האירוע?\nמחיקה תעבוד רק אם אין פעולות שמקושרות אליו."
        )

        if not confirm:
            return

        success, message = execute_query(
            "DELETE FROM public.events WHERE event_id = %s;",
            (event_id,)
        )

        if success:
            messagebox.showinfo("הצלחה", "האירוע נמחק בהצלחה")
            self.clear_event_form()
            self.refresh_all()
        else:
            messagebox.showerror(
                "לא ניתן למחוק",
                "לא ניתן למחוק את האירוע כי הוא כנראה מקושר לפעולות אחרות במסד."
            )

    def load_event_by_id(self):
        event_id = self.event_id_var.get().strip()

        if not event_id:
            messagebox.showwarning("שגיאה", "יש להזין Event ID")
            return

        row = fetch_one("""
            SELECT
                e.event_id,
                e.event_name,
                e.event_date,
                e.start_hour,
                e.end_hour,
                e.cost,
                e.status,
                e.order_num,
                t.trip_name,
                t.start_date
            FROM public.events e
            JOIN public.trips t
                ON e.trip_id = t.trip_id
            WHERE e.event_id = %s;
        """, (event_id,))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצא אירוע עם המזהה שהוזן")
            return

        self.event_id_var.set(row["event_id"])
        self.event_name_var.set(row["event_name"])
        self.event_date_var.set(row["event_date"])
        self.event_start_hour_var.set(row["start_hour"])
        self.event_end_hour_var.set(row["end_hour"])
        self.event_cost_var.set(row["cost"])
        self.event_status_var.set(row["status"])
        self.event_order_num_var.set(row["order_num"])
        self.event_trip_var.set(f"{row['trip_name']} | {row['start_date']}")

    # ---------------------------------------------------
    # Actions tab
    # ---------------------------------------------------
    def create_actions_tab(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי פעולה",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=12,
            pady=12
        )
        form_frame.pack(fill="x", padx=10, pady=8)

        fields = [
            ("Action ID", self.action_id_var, "entry", None),
            ("Action Name *", self.action_name_var, "entry", None),
            ("Action Type *", self.action_type_var, "combo_editable", ["Activity", "Meal", "Transport", "Safety", "Briefing", "Other"]),
            ("Address *", self.action_address_var, "entry", None),
            ("Event *", self.action_event_var, "combo", list(self.event_label_to_id.keys())),
        ]

        for index, (label_text, var, widget_type, options) in enumerate(fields):
            label = tk.Label(form_frame, text=label_text, font=("Arial", 10), bg=BG_COLOR)
            label.grid(row=index // 3, column=(index % 3) * 2, padx=8, pady=7, sticky="w")

            if widget_type == "combo":
                widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="readonly",
                    width=35,
                    font=("Arial", 10)
                )
                self.action_event_combo = widget
            elif widget_type == "combo_editable":
                widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="normal",
                    width=25,
                    font=("Arial", 10)
                )
            else:
                widget = tk.Entry(form_frame, textvariable=var, width=27, font=("Arial", 10))

            widget.grid(row=index // 3, column=(index % 3) * 2 + 1, padx=8, pady=7)

        actions_frame = tk.Frame(parent, bg=BG_COLOR)
        actions_frame.pack(fill="x", padx=10, pady=5)

        buttons = [
            ("שליפה לפי ID", self.load_action_by_id, BLUE, 16),
            ("הוספה", self.add_action, GREEN, 12),
            ("עדכון", self.update_action, ORANGE, 12),
            ("מחיקה", self.delete_action, RED, 12),
            ("ניקוי שדות", self.clear_action_form, GRAY, 14),
        ]

        for text, command, color, width in buttons:
            btn = create_button(actions_frame, text, command, color=color, width=width)
            btn.pack(side="left", padx=5)

        table_frame = tk.Frame(parent, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = [
            "action_id",
            "action_name",
            "action_type",
            "address",
            "event_name",
            "trip_name"
        ]

        headings = {
            "action_id": "Action ID",
            "action_name": "Action Name",
            "action_type": "Type",
            "address": "Address",
            "event_name": "Event",
            "trip_name": "Trip"
        }

        self.action_tree = create_table(table_frame, columns, headings)
        self.action_tree.bind("<<TreeviewSelect>>", self.on_action_select)

    def load_actions_table(self):
        if self.action_tree is None:
            return

        for item in self.action_tree.get_children():
            self.action_tree.delete(item)

        rows = fetch_all("""
            SELECT
                a.action_id,
                a.action_name,
                a.action_type,
                a.address,
                e.event_name,
                t.trip_name
            FROM public.actions a
            JOIN public.events e
                ON a.event_id = e.event_id
            JOIN public.trips t
                ON e.trip_id = t.trip_id
            ORDER BY a.action_id;
        """)

        for row in rows:
            self.action_tree.insert(
                "",
                "end",
                values=[
                    row["action_id"],
                    row["action_name"],
                    row["action_type"],
                    row["address"],
                    row["event_name"],
                    row["trip_name"]
                ]
            )

    def clear_action_form(self):
        self.action_id_var.set("")
        self.action_name_var.set("")
        self.action_type_var.set("")
        self.action_address_var.set("")
        self.action_event_var.set("")

    def on_action_select(self, event):
        selected = self.action_tree.selection()
        if not selected:
            return

        values = self.action_tree.item(selected[0], "values")
        self.action_id_var.set(values[0])
        self.action_name_var.set(values[1])
        self.action_type_var.set(values[2])
        self.action_address_var.set(values[3])

        row = fetch_one("""
            SELECT
                e.event_name,
                e.event_date,
                t.trip_name
            FROM public.actions a
            JOIN public.events e
                ON a.event_id = e.event_id
            JOIN public.trips t
                ON e.trip_id = t.trip_id
            WHERE a.action_id = %s;
        """, (values[0],))

        if row:
            self.action_event_var.set(f"{row['event_name']} | {row['event_date']} | {row['trip_name']}")

    def get_next_action_id(self):
        row = fetch_one("""
            SELECT COALESCE(MAX(action_id), 0) + 1 AS next_id
            FROM public.actions;
        """)
        return 1 if row is None else row["next_id"]

    def validate_action_form(self, require_id=False):
        if require_id and not self.action_id_var.get().strip():
            messagebox.showwarning("שגיאה", "יש להזין Action ID")
            return False

        required = [
            (self.action_name_var.get().strip(), "Action Name"),
            (self.action_type_var.get().strip(), "Action Type"),
            (self.action_address_var.get().strip(), "Address"),
            (self.action_event_var.get().strip(), "Event"),
        ]

        for value, name in required:
            if value == "":
                messagebox.showwarning("שגיאה", f"יש למלא את השדה: {name}")
                return False

        if self.action_event_var.get().strip() not in self.event_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Event מתוך הרשימה")
            return False

        return True

    def add_action(self):
        if not self.validate_action_form(require_id=False):
            return

        action_id = self.action_id_var.get().strip()
        if action_id == "":
            action_id = self.get_next_action_id()

        event_id = self.event_label_to_id[self.action_event_var.get().strip()]

        query = """
            INSERT INTO public.actions
                (action_id, address, action_type, action_name, event_id)
            VALUES
                (%s, %s, %s, %s, %s);
        """

        params = (
            action_id,
            self.action_address_var.get().strip(),
            self.action_type_var.get().strip(),
            self.action_name_var.get().strip(),
            event_id
        )

        success, message = execute_query(query, params)

        if success:
            messagebox.showinfo("הצלחה", "הפעולה נוספה בהצלחה")
            self.clear_action_form()
            self.load_actions_table()
        else:
            messagebox.showerror("שגיאה", message)

    def update_action(self):
        if not self.validate_action_form(require_id=True):
            return

        event_id = self.event_label_to_id[self.action_event_var.get().strip()]

        query = """
            UPDATE public.actions
            SET
                address = %s,
                action_type = %s,
                action_name = %s,
                event_id = %s
            WHERE action_id = %s;
        """

        params = (
            self.action_address_var.get().strip(),
            self.action_type_var.get().strip(),
            self.action_name_var.get().strip(),
            event_id,
            self.action_id_var.get().strip()
        )

        success, message = execute_query(query, params)

        if success:
            messagebox.showinfo("הצלחה", "הפעולה עודכנה בהצלחה")
            self.load_actions_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_action(self):
        action_id = self.action_id_var.get().strip()

        if not action_id:
            messagebox.showwarning("שגיאה", "יש להזין Action ID למחיקה")
            return

        confirm = messagebox.askyesno("אישור מחיקה", "האם למחוק את הפעולה?")
        if not confirm:
            return

        success, message = execute_query(
            "DELETE FROM public.actions WHERE action_id = %s;",
            (action_id,)
        )

        if success:
            messagebox.showinfo("הצלחה", "הפעולה נמחקה בהצלחה")
            self.clear_action_form()
            self.load_actions_table()
        else:
            messagebox.showerror("שגיאה", message)

    def load_action_by_id(self):
        action_id = self.action_id_var.get().strip()

        if not action_id:
            messagebox.showwarning("שגיאה", "יש להזין Action ID")
            return

        row = fetch_one("""
            SELECT
                a.action_id,
                a.action_name,
                a.action_type,
                a.address,
                e.event_name,
                e.event_date,
                t.trip_name
            FROM public.actions a
            JOIN public.events e
                ON a.event_id = e.event_id
            JOIN public.trips t
                ON e.trip_id = t.trip_id
            WHERE a.action_id = %s;
        """, (action_id,))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצאה פעולה עם המזהה שהוזן")
            return

        self.action_id_var.set(row["action_id"])
        self.action_name_var.set(row["action_name"])
        self.action_type_var.set(row["action_type"])
        self.action_address_var.set(row["address"])
        self.action_event_var.set(f"{row['event_name']} | {row['event_date']} | {row['trip_name']}")

    # ---------------------------------------------------
    # Schedules tab
    # ---------------------------------------------------
    def create_schedules_tab(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי לו״ז",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=12,
            pady=12
        )
        form_frame.pack(fill="x", padx=10, pady=8)

        fields = [
            ("Trip *", self.schedule_trip_var, "combo", list(self.trip_label_to_id.keys())),
            ("Order Number *", self.schedule_order_num_var, "entry", None),
            ("Schedule Date YYYY-MM-DD *", self.schedule_date_var, "entry", None),
            ("Start Time HH:MM *", self.schedule_start_time_var, "entry", None),
            ("End Time HH:MM *", self.schedule_end_time_var, "entry", None),
            ("Description *", self.schedule_description_var, "entry", None),
        ]

        for index, (label_text, var, widget_type, options) in enumerate(fields):
            label = tk.Label(form_frame, text=label_text, font=("Arial", 10), bg=BG_COLOR)
            label.grid(row=index // 3, column=(index % 3) * 2, padx=8, pady=7, sticky="w")

            if widget_type == "combo":
                widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="readonly",
                    width=35,
                    font=("Arial", 10)
                )
                self.schedule_trip_combo = widget
            else:
                widget = tk.Entry(form_frame, textvariable=var, width=27, font=("Arial", 10))

            widget.grid(row=index // 3, column=(index % 3) * 2 + 1, padx=8, pady=7)

        actions_frame = tk.Frame(parent, bg=BG_COLOR)
        actions_frame.pack(fill="x", padx=10, pady=5)

        buttons = [
            ("שליפה לפי Trip + Order", self.load_schedule_by_key, BLUE, 22),
            ("הוספה", self.add_schedule, GREEN, 12),
            ("עדכון", self.update_schedule, ORANGE, 12),
            ("מחיקה", self.delete_schedule, RED, 12),
            ("ניקוי שדות", self.clear_schedule_form, GRAY, 14),
        ]

        for text, command, color, width in buttons:
            btn = create_button(actions_frame, text, command, color=color, width=width)
            btn.pack(side="left", padx=5)

        table_frame = tk.Frame(parent, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = [
            "trip_name",
            "order_num",
            "sch_date",
            "start_time",
            "end_time",
            "description"
        ]

        headings = {
            "trip_name": "Trip",
            "order_num": "Order",
            "sch_date": "Date",
            "start_time": "Start",
            "end_time": "End",
            "description": "Description"
        }

        self.schedule_tree = create_table(table_frame, columns, headings)
        self.schedule_tree.bind("<<TreeviewSelect>>", self.on_schedule_select)

    def load_schedules_table(self):
        if self.schedule_tree is None:
            return

        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)

        rows = fetch_all("""
            SELECT
                t.trip_name,
                t.start_date AS trip_start_date,
                s.order_num,
                s.sch_date,
                s.start_time,
                s.end_time,
                s.description
            FROM public.schedules s
            JOIN public.trips t
                ON s.trip_id = t.trip_id
            ORDER BY s.trip_id, s.order_num;
        """)

        for row in rows:
            self.schedule_tree.insert(
                "",
                "end",
                values=[
                    row["trip_name"],
                    row["order_num"],
                    row["sch_date"],
                    row["start_time"],
                    row["end_time"],
                    row["description"]
                ]
            )

    def clear_schedule_form(self):
        self.schedule_trip_var.set("")
        self.schedule_order_num_var.set("")
        self.schedule_date_var.set("")
        self.schedule_start_time_var.set("")
        self.schedule_end_time_var.set("")
        self.schedule_description_var.set("")

    def on_schedule_select(self, event):
        selected = self.schedule_tree.selection()
        if not selected:
            return

        values = self.schedule_tree.item(selected[0], "values")

        trip_name = values[0]
        order_num = values[1]

        row = fetch_one("""
            SELECT
                t.trip_name,
                t.start_date,
                s.order_num,
                s.sch_date,
                s.start_time,
                s.end_time,
                s.description
            FROM public.schedules s
            JOIN public.trips t
                ON s.trip_id = t.trip_id
            WHERE t.trip_name = %s
              AND s.order_num = %s
            LIMIT 1;
        """, (trip_name, order_num))

        if row:
            self.schedule_trip_var.set(f"{row['trip_name']} | {row['start_date']}")
            self.schedule_order_num_var.set(row["order_num"])
            self.schedule_date_var.set(row["sch_date"])
            self.schedule_start_time_var.set(row["start_time"])
            self.schedule_end_time_var.set(row["end_time"])
            self.schedule_description_var.set(row["description"])

    def validate_schedule_form(self):
        required = [
            (self.schedule_trip_var.get().strip(), "Trip"),
            (self.schedule_order_num_var.get().strip(), "Order Number"),
            (self.schedule_date_var.get().strip(), "Schedule Date"),
            (self.schedule_start_time_var.get().strip(), "Start Time"),
            (self.schedule_end_time_var.get().strip(), "End Time"),
            (self.schedule_description_var.get().strip(), "Description"),
        ]

        for value, name in required:
            if value == "":
                messagebox.showwarning("שגיאה", f"יש למלא את השדה: {name}")
                return False

        if self.schedule_trip_var.get().strip() not in self.trip_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Trip מתוך הרשימה")
            return False

        try:
            int(self.schedule_order_num_var.get().strip())
        except ValueError:
            messagebox.showwarning("שגיאה", "Order Number חייב להיות מספר שלם")
            return False

        return True

    def add_schedule(self):
        if not self.validate_schedule_form():
            return

        trip_id = self.trip_label_to_id[self.schedule_trip_var.get().strip()]

        query = """
            INSERT INTO public.schedules
                (trip_id, order_num, start_time, end_time, description, sch_date)
            VALUES
                (%s, %s, %s, %s, %s, %s);
        """

        params = (
            trip_id,
            self.schedule_order_num_var.get().strip(),
            self.schedule_start_time_var.get().strip(),
            self.schedule_end_time_var.get().strip(),
            self.schedule_description_var.get().strip(),
            self.schedule_date_var.get().strip()
        )

        success, message = execute_query(query, params)

        if success:
            messagebox.showinfo("הצלחה", "רשומת הלו״ז נוספה בהצלחה")
            self.clear_schedule_form()
            self.load_schedules_table()
        else:
            messagebox.showerror("שגיאה", message)

    def update_schedule(self):
        if not self.validate_schedule_form():
            return

        trip_id = self.trip_label_to_id[self.schedule_trip_var.get().strip()]

        query = """
            UPDATE public.schedules
            SET
                start_time = %s,
                end_time = %s,
                description = %s,
                sch_date = %s
            WHERE trip_id = %s
              AND order_num = %s;
        """

        params = (
            self.schedule_start_time_var.get().strip(),
            self.schedule_end_time_var.get().strip(),
            self.schedule_description_var.get().strip(),
            self.schedule_date_var.get().strip(),
            trip_id,
            self.schedule_order_num_var.get().strip()
        )

        success, message = execute_query(query, params)

        if success:
            messagebox.showinfo("הצלחה", "רשומת הלו״ז עודכנה בהצלחה")
            self.load_schedules_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_schedule(self):
        if not self.validate_schedule_form():
            return

        confirm = messagebox.askyesno("אישור מחיקה", "האם למחוק את רשומת הלו״ז?")
        if not confirm:
            return

        trip_id = self.trip_label_to_id[self.schedule_trip_var.get().strip()]

        query = """
            DELETE FROM public.schedules
            WHERE trip_id = %s
              AND order_num = %s;
        """

        success, message = execute_query(
            query,
            (trip_id, self.schedule_order_num_var.get().strip())
        )

        if success:
            messagebox.showinfo("הצלחה", "רשומת הלו״ז נמחקה בהצלחה")
            self.clear_schedule_form()
            self.load_schedules_table()
        else:
            messagebox.showerror("שגיאה", message)

    def load_schedule_by_key(self):
        if not self.schedule_trip_var.get().strip() or not self.schedule_order_num_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Trip ולהזין Order Number")
            return

        if self.schedule_trip_var.get().strip() not in self.trip_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Trip מתוך הרשימה")
            return

        trip_id = self.trip_label_to_id[self.schedule_trip_var.get().strip()]

        row = fetch_one("""
            SELECT
                t.trip_name,
                t.start_date,
                s.order_num,
                s.sch_date,
                s.start_time,
                s.end_time,
                s.description
            FROM public.schedules s
            JOIN public.trips t
                ON s.trip_id = t.trip_id
            WHERE s.trip_id = %s
              AND s.order_num = %s;
        """, (trip_id, self.schedule_order_num_var.get().strip()))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצאה רשומת לו״ז עבור הטיול והסדר שהוזנו")
            return

        self.schedule_trip_var.set(f"{row['trip_name']} | {row['start_date']}")
        self.schedule_order_num_var.set(row["order_num"])
        self.schedule_date_var.set(row["sch_date"])
        self.schedule_start_time_var.set(row["start_time"])
        self.schedule_end_time_var.set(row["end_time"])
        self.schedule_description_var.set(row["description"])