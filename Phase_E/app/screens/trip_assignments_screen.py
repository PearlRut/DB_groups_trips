# screens/trip_assignments_screen.py

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


class TripAssignmentsScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        self.tree = None

        self.trip_var = tk.StringVar()
        self.participant_var = tk.StringVar()

        self.trip_label_to_id = {}
        self.participant_label_to_id = {}

        self.trip_id_to_label = {}
        self.participant_id_to_label = {}

        self.selected_old_trip_id = None
        self.selected_old_participant_id = None

        self.trip_combo = None
        self.participant_combo = None

    def show(self):
        self.app.clear_screen()

        create_title(self.root, "שיבוץ משתתפים לטיולים")

        self.load_reference_data()

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_form(main_frame)
        self.create_actions(main_frame)
        self.create_table_area(main_frame)
        self.create_bottom_buttons()

        self.load_table()

    def load_reference_data(self):
        self.trip_label_to_id = {}
        self.participant_label_to_id = {}
        self.trip_id_to_label = {}
        self.participant_id_to_label = {}

        trips = fetch_all("""
            SELECT trip_id, trip_name, start_date
            FROM public.trips
            ORDER BY trip_name, start_date;
        """)

        for row in trips:
            label = f"{row['trip_name']} | {row['start_date']}"
            self.trip_label_to_id[label] = row["trip_id"]
            self.trip_id_to_label[row["trip_id"]] = label

        participants = fetch_all("""
            SELECT participant_id, first_name, last_name, phone
            FROM public.participants
            ORDER BY first_name, last_name;
        """)

        for row in participants:
            label = f"{row['first_name']} {row['last_name']} | {row['phone']}"
            self.participant_label_to_id[label] = row["participant_id"]
            self.participant_id_to_label[row["participant_id"]] = label

    def create_form(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי שיבוץ",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=15,
            pady=15
        )
        form_frame.pack(fill="x", pady=10)

        trip_label = tk.Label(
            form_frame,
            text="Trip *",
            font=("Arial", 10),
            bg=BG_COLOR
        )
        trip_label.grid(row=0, column=0, padx=8, pady=8, sticky="w")

        self.trip_combo = ttk.Combobox(
            form_frame,
            textvariable=self.trip_var,
            values=list(self.trip_label_to_id.keys()),
            state="readonly",
            width=40,
            font=("Arial", 10)
        )
        self.trip_combo.grid(row=0, column=1, padx=8, pady=8)

        participant_label = tk.Label(
            form_frame,
            text="Participant *",
            font=("Arial", 10),
            bg=BG_COLOR
        )
        participant_label.grid(row=0, column=2, padx=8, pady=8, sticky="w")

        self.participant_combo = ttk.Combobox(
            form_frame,
            textvariable=self.participant_var,
            values=list(self.participant_label_to_id.keys()),
            state="readonly",
            width=40,
            font=("Arial", 10)
        )
        self.participant_combo.grid(row=0, column=3, padx=8, pady=8)

    def create_actions(self, parent):
        actions_frame = tk.Frame(parent, bg=BG_COLOR)
        actions_frame.pack(fill="x", pady=10)

        buttons = [
            ("שליפה לפי טיול ומשתתף", self.load_by_selection, BLUE, 22),
            ("הוספה", self.add_assignment, GREEN, 14),
            ("עדכון", self.update_assignment, ORANGE, 14),
            ("מחיקה", self.delete_assignment, RED, 14),
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
            "trip_name",
            "trip_start_date",
            "participant_name",
            "phone",
            "email",
            "trip_status"
        ]

        headings = {
            "trip_name": "Trip",
            "trip_start_date": "Trip Start Date",
            "participant_name": "Participant",
            "phone": "Phone",
            "email": "Email",
            "trip_status": "Trip Status"
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
        self.load_reference_data()

        if self.trip_combo is not None:
            self.trip_combo["values"] = list(self.trip_label_to_id.keys())

        if self.participant_combo is not None:
            self.participant_combo["values"] = list(self.participant_label_to_id.keys())

        self.load_table()

    def load_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT
                t.trip_id,
                t.trip_name,
                t.start_date,
                t.status,
                p.participant_id,
                p.first_name,
                p.last_name,
                p.phone,
                p.email
            FROM public.trip_participants tp
            JOIN public.trips t
                ON tp.trip_id = t.trip_id
            JOIN public.participants p
                ON tp.participant_id = p.participant_id
            ORDER BY t.trip_id, p.first_name, p.last_name;
        """

        rows = fetch_all(query)

        for row in rows:
            participant_name = f"{row['first_name']} {row['last_name']}"
            item_id = f"{row['trip_id']}|{row['participant_id']}"

            self.tree.insert(
                "",
                "end",
                iid=item_id,
                values=[
                    row["trip_name"],
                    row["start_date"],
                    participant_name,
                    row["phone"],
                    row["email"],
                    row["status"]
                ]
            )

    def clear_form(self):
        self.trip_var.set("")
        self.participant_var.set("")
        self.selected_old_trip_id = None
        self.selected_old_participant_id = None

    def validate_form(self):
        if not self.trip_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Trip")
            return False

        if self.trip_var.get().strip() not in self.trip_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Trip מתוך הרשימה")
            return False

        if not self.participant_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Participant")
            return False

        if self.participant_var.get().strip() not in self.participant_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Participant מתוך הרשימה")
            return False

        return True

    def on_select(self, event):
        selected = self.tree.selection()

        if not selected:
            return

        item_id = selected[0]

        try:
            trip_id_text, participant_id_text = item_id.split("|")
            trip_id = int(trip_id_text)
            participant_id = int(participant_id_text)
        except ValueError:
            messagebox.showerror("שגיאה", "לא ניתן לקרוא את השיבוץ שנבחר")
            return

        self.selected_old_trip_id = trip_id
        self.selected_old_participant_id = participant_id

        if trip_id in self.trip_id_to_label:
            self.trip_var.set(self.trip_id_to_label[trip_id])

        if participant_id in self.participant_id_to_label:
            self.participant_var.set(self.participant_id_to_label[participant_id])

    def load_by_selection(self):
        if not self.validate_form():
            return

        trip_id = self.trip_label_to_id[self.trip_var.get().strip()]
        participant_id = self.participant_label_to_id[self.participant_var.get().strip()]

        query = """
            SELECT
                t.trip_id,
                t.trip_name,
                t.start_date,
                p.participant_id,
                p.first_name,
                p.last_name,
                p.phone
            FROM public.trip_participants tp
            JOIN public.trips t
                ON tp.trip_id = t.trip_id
            JOIN public.participants p
                ON tp.participant_id = p.participant_id
            WHERE tp.trip_id = %s
              AND tp.participant_id = %s;
        """

        row = fetch_one(query, (trip_id, participant_id))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצא שיבוץ כזה")
            return

        self.selected_old_trip_id = row["trip_id"]
        self.selected_old_participant_id = row["participant_id"]

        messagebox.showinfo(
            "נמצא",
            "השיבוץ נמצא ונטען.\nכעת ניתן לעדכן או למחוק אותו."
        )

    def add_assignment(self):
        if not self.validate_form():
            return

        trip_id = self.trip_label_to_id[self.trip_var.get().strip()]
        participant_id = self.participant_label_to_id[self.participant_var.get().strip()]

        query = """
            INSERT INTO public.trip_participants
                (trip_id, participant_id)
            VALUES
                (%s, %s);
        """

        success, message = execute_query(query, (trip_id, participant_id))

        if success:
            messagebox.showinfo(
                "הצלחה",
                "המשתתף שובץ לטיול בהצלחה.\nאפשר לבדוק עכשיו את דוח התפוסה במסך הדוחות."
            )
            self.clear_form()
            self.refresh_screen()
        else:
            messagebox.showerror(
                "שגיאה",
                "לא ניתן להוסיף את השיבוץ.\n"
                "יכול להיות שהמשתתף כבר משובץ לטיול הזה או שיש בעיית נתונים.\n\n"
                f"{message}"
            )

    def update_assignment(self):
        if not self.validate_form():
            return

        if self.selected_old_trip_id is None or self.selected_old_participant_id is None:
            messagebox.showwarning(
                "שגיאה",
                "לעדכון צריך קודם לבחור שיבוץ מהטבלה או לבצע שליפה לפי טיול ומשתתף."
            )
            return

        new_trip_id = self.trip_label_to_id[self.trip_var.get().strip()]
        new_participant_id = self.participant_label_to_id[self.participant_var.get().strip()]

        query = """
            UPDATE public.trip_participants
            SET
                trip_id = %s,
                participant_id = %s
            WHERE trip_id = %s
              AND participant_id = %s;
        """

        params = (
            new_trip_id,
            new_participant_id,
            self.selected_old_trip_id,
            self.selected_old_participant_id
        )

        success, message = execute_query(query, params)

        if success:
            messagebox.showinfo("הצלחה", "השיבוץ עודכן בהצלחה")
            self.clear_form()
            self.refresh_screen()
        else:
            messagebox.showerror(
                "שגיאה",
                "לא ניתן לעדכן את השיבוץ.\n"
                "יכול להיות שהשיבוץ החדש כבר קיים.\n\n"
                f"{message}"
            )

    def delete_assignment(self):
        if not self.validate_form():
            return

        trip_id = self.trip_label_to_id[self.trip_var.get().strip()]
        participant_id = self.participant_label_to_id[self.participant_var.get().strip()]

        confirm = messagebox.askyesno(
            "אישור מחיקה",
            "האם למחוק את השיבוץ של המשתתף לטיול?"
        )

        if not confirm:
            return

        query = """
            DELETE FROM public.trip_participants
            WHERE trip_id = %s
              AND participant_id = %s;
        """

        success, message = execute_query(query, (trip_id, participant_id))

        if success:
            messagebox.showinfo(
                "הצלחה",
                "השיבוץ נמחק בהצלחה.\nאפשר לבדוק עכשיו את דוח התפוסה במסך הדוחות."
            )
            self.clear_form()
            self.refresh_screen()
        else:
            messagebox.showerror("שגיאה", message)