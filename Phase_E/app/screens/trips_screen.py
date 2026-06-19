# screens/trips_screen.py

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


class TripsScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        self.tree = None

        self.trip_id_var = tk.StringVar()
        self.trip_name_var = tk.StringVar()
        self.trip_type_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.group_size_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.route_var = tk.StringVar()
        self.transport_type_var = tk.StringVar()

        self.route_name_to_id = {}
        self.transport_type_name_to_id = {}

    def show(self):
        self.app.clear_screen()

        create_title(self.root, "ניהול טיולים")

        self.load_combo_data()

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_form(main_frame)
        self.create_actions(main_frame)
        self.create_table_area(main_frame)
        self.create_bottom_buttons()

        self.load_table()

    def load_combo_data(self):
        self.route_name_to_id = {}
        self.transport_type_name_to_id = {}

        routes = fetch_all("""
            SELECT route_id, route_name
            FROM public.routes
            ORDER BY route_name;
        """)

        for row in routes:
            self.route_name_to_id[row["route_name"]] = row["route_id"]

        transport_types = fetch_all("""
            SELECT transport_type_id, transport_type_name
            FROM public.transport_types
            ORDER BY transport_type_name;
        """)

        for row in transport_types:
            self.transport_type_name_to_id[row["transport_type_name"]] = row["transport_type_id"]

    def create_form(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי טיול",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=15,
            pady=15
        )
        form_frame.pack(fill="x", pady=10)

        fields = [
            ("Trip ID", self.trip_id_var, "entry", None),
            ("Trip Name *", self.trip_name_var, "entry", None),
            ("Trip Type *", self.trip_type_var, "combo_editable", ["One Day", "Camping", "Family", "Adventure", "Educational", "Other"]),
            ("Start Date YYYY-MM-DD *", self.start_date_var, "entry", None),
            ("End Date YYYY-MM-DD *", self.end_date_var, "entry", None),
            ("Group Size *", self.group_size_var, "entry", None),

            # OVERBOOKED is not here because it is calculated by the procedure,
            # not selected manually by the user.
            ("Status *", self.status_var, "combo_readonly", ["PLANNED", "OPEN", "COMPLETED"]),

            ("Route *", self.route_var, "combo_readonly", list(self.route_name_to_id.keys())),
            ("Transport Type *", self.transport_type_var, "combo_readonly", list(self.transport_type_name_to_id.keys())),
        ]

        for index, (label_text, var, widget_type, options) in enumerate(fields):
            label = tk.Label(
                form_frame,
                text=label_text,
                font=("Arial", 10),
                bg=BG_COLOR
            )
            label.grid(
                row=index // 3,
                column=(index % 3) * 2,
                padx=8,
                pady=8,
                sticky="w"
            )

            if widget_type == "combo_readonly":
                input_widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="readonly",
                    width=23,
                    font=("Arial", 10)
                )
            elif widget_type == "combo_editable":
                input_widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="normal",
                    width=23,
                    font=("Arial", 10)
                )
            else:
                input_widget = tk.Entry(
                    form_frame,
                    textvariable=var,
                    width=25,
                    font=("Arial", 10)
                )

            input_widget.grid(
                row=index // 3,
                column=(index % 3) * 2 + 1,
                padx=8,
                pady=8
            )

    def create_actions(self, parent):
        actions_frame = tk.Frame(parent, bg=BG_COLOR)
        actions_frame.pack(fill="x", pady=10)

        buttons = [
            ("שליפה לפי ID", self.load_by_id, BLUE, 16),
            ("הוספה", self.add_trip, GREEN, 14),
            ("עדכון", self.update_trip, ORANGE, 14),
            ("מחיקה", self.delete_trip, RED, 14),
            ("ניקוי שדות", self.clear_form, GRAY, 14),
        ]

        for text, command, color, width in buttons:
            btn = create_button(
                actions_frame,
                text,
                command,
                color=color,
                width=width
            )
            btn.pack(side="left", padx=5)

    def create_table_area(self, parent):
        table_frame = tk.Frame(parent, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, pady=10)

        columns = [
            "trip_id",
            "trip_name",
            "trip_type",
            "start_date",
            "end_date",
            "group_size",
            "status",
            "route_name",
            "transport_type_name"
        ]

        headings = {
            "trip_id": "Trip ID",
            "trip_name": "Trip Name",
            "trip_type": "Trip Type",
            "start_date": "Start Date",
            "end_date": "End Date",
            "group_size": "Group Size",
            "status": "Status",
            "route_name": "Route",
            "transport_type_name": "Transport Type"
        }

        self.tree = create_table(table_frame, columns, headings)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

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
            self.refresh_screen,
            color=GREEN,
            width=15
        )
        refresh_btn.pack(side="left", padx=10)

    def refresh_screen(self):
        self.load_combo_data()
        self.load_table()

    def load_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT
                t.trip_id,
                t.trip_name,
                t.trip_type,
                t.start_date,
                t.end_date,
                t.group_size,
                t.status,
                r.route_name,
                tt.transport_type_name
            FROM public.trips t
            JOIN public.routes r
                ON t.route_id = r.route_id
            JOIN public.transport_types tt
                ON t.transport_type_id = tt.transport_type_id
            ORDER BY t.trip_id;
        """

        rows = fetch_all(query)

        for row in rows:
            self.tree.insert(
                "",
                "end",
                values=[
                    row["trip_id"],
                    row["trip_name"],
                    row["trip_type"],
                    row["start_date"],
                    row["end_date"],
                    row["group_size"],
                    row["status"],
                    row["route_name"],
                    row["transport_type_name"]
                ]
            )

    def clear_form(self):
        self.trip_id_var.set("")
        self.trip_name_var.set("")
        self.trip_type_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.group_size_var.set("")
        self.status_var.set("")
        self.route_var.set("")
        self.transport_type_var.set("")

    def on_select(self, event):
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")

        self.trip_id_var.set(values[0])
        self.trip_name_var.set(values[1])
        self.trip_type_var.set(values[2])
        self.start_date_var.set(values[3])
        self.end_date_var.set(values[4])
        self.group_size_var.set(values[5])
        self.status_var.set(values[6])
        self.route_var.set(values[7])
        self.transport_type_var.set(values[8])

    def validate_form(self, require_id=False):
        if require_id and not self.trip_id_var.get().strip():
            messagebox.showwarning("שגיאה", "יש להזין Trip ID")
            return False

        required_values = [
            (self.trip_name_var.get().strip(), "Trip Name"),
            (self.trip_type_var.get().strip(), "Trip Type"),
            (self.start_date_var.get().strip(), "Start Date"),
            (self.end_date_var.get().strip(), "End Date"),
            (self.group_size_var.get().strip(), "Group Size"),
            (self.status_var.get().strip(), "Status"),
            (self.route_var.get().strip(), "Route"),
            (self.transport_type_var.get().strip(), "Transport Type"),
        ]

        for value, field_name in required_values:
            if value == "":
                messagebox.showwarning("שגיאה", f"יש למלא את השדה: {field_name}")
                return False

        if self.route_var.get().strip() not in self.route_name_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Route מתוך הרשימה")
            return False

        if self.transport_type_var.get().strip() not in self.transport_type_name_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Transport Type מתוך הרשימה")
            return False

        try:
            int(self.group_size_var.get().strip())
        except ValueError:
            messagebox.showwarning("שגיאה", "Group Size חייב להיות מספר שלם")
            return False

        return True

    def get_form_values(self):
        route_id = self.route_name_to_id[self.route_var.get().strip()]
        transport_type_id = self.transport_type_name_to_id[self.transport_type_var.get().strip()]

        return {
            "trip_name": self.trip_name_var.get().strip(),
            "trip_type": self.trip_type_var.get().strip(),
            "start_date": self.start_date_var.get().strip(),
            "end_date": self.end_date_var.get().strip(),
            "group_size": int(self.group_size_var.get().strip()),
            "status": self.status_var.get().strip(),
            "route_id": route_id,
            "transport_type_id": transport_type_id
        }

    def load_by_id(self):
        trip_id = self.trip_id_var.get().strip()

        if not trip_id:
            messagebox.showwarning("שגיאה", "יש להזין Trip ID")
            return

        query = """
            SELECT
                t.trip_id,
                t.trip_name,
                t.trip_type,
                t.start_date,
                t.end_date,
                t.group_size,
                t.status,
                r.route_name,
                tt.transport_type_name
            FROM public.trips t
            JOIN public.routes r
                ON t.route_id = r.route_id
            JOIN public.transport_types tt
                ON t.transport_type_id = tt.transport_type_id
            WHERE t.trip_id = %s;
        """

        row = fetch_one(query, (trip_id,))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצא טיול עם המזהה שהוזן")
            return

        self.trip_id_var.set(row["trip_id"])
        self.trip_name_var.set(row["trip_name"])
        self.trip_type_var.set(row["trip_type"])
        self.start_date_var.set(row["start_date"])
        self.end_date_var.set(row["end_date"])
        self.group_size_var.set(row["group_size"])
        self.status_var.set(row["status"])
        self.route_var.set(row["route_name"])
        self.transport_type_var.set(row["transport_type_name"])

    def add_trip(self):
        if not self.validate_form(require_id=False):
            return

        values = self.get_form_values()

        query = """
            INSERT INTO public.trips
                (trip_name, start_date, end_date, group_size, status, route_id, transport_type_id, trip_type)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s);
        """

        params = (
            values["trip_name"],
            values["start_date"],
            values["end_date"],
            values["group_size"],
            values["status"],
            values["route_id"],
            values["transport_type_id"],
            values["trip_type"]
        )

        success, message = execute_query(query, params)

        if success:
            messagebox.showinfo("הצלחה", "הטיול נוסף בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)

    def update_trip(self):
        if not self.validate_form(require_id=True):
            return

        values = self.get_form_values()
        trip_id = self.trip_id_var.get().strip()

        query = """
            UPDATE public.trips
            SET
                trip_name = %s,
                start_date = %s,
                end_date = %s,
                group_size = %s,
                status = %s,
                route_id = %s,
                transport_type_id = %s,
                trip_type = %s
            WHERE trip_id = %s;
        """

        params = (
            values["trip_name"],
            values["start_date"],
            values["end_date"],
            values["group_size"],
            values["status"],
            values["route_id"],
            values["transport_type_id"],
            values["trip_type"],
            trip_id
        )

        success, message = execute_query(query, params)

        if success:
            messagebox.showinfo("הצלחה", "הטיול עודכן בהצלחה")
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_trip(self):
        trip_id = self.trip_id_var.get().strip()

        if not trip_id:
            messagebox.showwarning("שגיאה", "למחיקה יש להזין Trip ID")
            return

        confirm = messagebox.askyesno(
            "אישור מחיקה",
            "האם את בטוחה שברצונך למחוק את הטיול?\n"
            "מחיקה תתאפשר רק אם הטיול אינו מקושר לרשומות אחרות."
        )

        if not confirm:
            return

        query = """
            DELETE FROM public.trips
            WHERE trip_id = %s;
        """

        success, message = execute_query(query, (trip_id,))

        if success:
            messagebox.showinfo("הצלחה", "הטיול נמחק בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror(
                "לא ניתן למחוק",
                "לא ניתן למחוק את הטיול כי הוא מקושר לרשומות אחרות במסד הנתונים.\n\n"
                "זה תקין: בסיס הנתונים שומר על שלמות הנתונים בעזרת Foreign Keys.\n"
                "כדי למחוק טיול, קודם צריך למחוק את הרשומות המקושרות אליו."
            )