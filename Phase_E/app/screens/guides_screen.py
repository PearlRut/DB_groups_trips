# screens/guides_screen.py

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


class GuidesScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        self.tree = None

        self.participant_var = tk.StringVar()
        self.license_number_var = tk.StringVar()
        self.experience_years_var = tk.StringVar()

        self.participant_label_to_id = {}

    def show(self):
        self.app.clear_screen()

        create_title(self.root, "ניהול מדריכים")

        self.load_participants_data()

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_form(main_frame)
        self.create_actions(main_frame)
        self.create_table_area(main_frame)
        self.create_bottom_buttons()

        self.load_table()

    def load_participants_data(self):
        self.participant_label_to_id = {}

        participants = fetch_all("""
            SELECT participant_id, first_name, last_name, phone
            FROM public.participants
            ORDER BY first_name, last_name;
        """)

        for row in participants:
            label = f"{row['first_name']} {row['last_name']} | {row['phone']}"
            self.participant_label_to_id[label] = row["participant_id"]

    def create_form(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי מדריך",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=15,
            pady=15
        )
        form_frame.pack(fill="x", pady=10)

        fields = [
            ("Participant *", self.participant_var, "combo", list(self.participant_label_to_id.keys())),
            ("License Number *", self.license_number_var, "entry", None),
            ("Experience Years *", self.experience_years_var, "entry", None),
        ]

        for index, (label_text, var, widget_type, options) in enumerate(fields):
            label = tk.Label(
                form_frame,
                text=label_text,
                font=("Arial", 10),
                bg=BG_COLOR
            )
            label.grid(
                row=0,
                column=index * 2,
                padx=8,
                pady=8,
                sticky="w"
            )

            if widget_type == "combo":
                input_widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="readonly",
                    width=35,
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
                row=0,
                column=index * 2 + 1,
                padx=8,
                pady=8
            )

    def create_actions(self, parent):
        actions_frame = tk.Frame(parent, bg=BG_COLOR)
        actions_frame.pack(fill="x", pady=10)

        buttons = [
            ("שליפה לפי משתתף", self.load_by_participant, BLUE, 18),
            ("הוספה", self.add_guide, GREEN, 14),
            ("עדכון", self.update_guide, ORANGE, 14),
            ("מחיקה", self.delete_guide, RED, 14),
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
            "participant_name",
            "phone",
            "email",
            "license_number",
            "experience_years"
        ]

        headings = {
            "participant_name": "Guide Name",
            "phone": "Phone",
            "email": "Email",
            "license_number": "License Number",
            "experience_years": "Experience Years"
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
        self.load_participants_data()
        self.load_table()

    def load_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        # שאילתת SELECT לשליפת כלל המדריכים.
        # טבלת guides היא ישות תת-טיפוס (Subtype) של participants (קשר ירושה של 1 ל-1).
        # אנו מבצעים JOIN כדי לקבל את פרטיהם האישיים של המדריכים מטבלת המשתתפים.
        query = """
            SELECT
                p.first_name,
                p.last_name,
                p.phone,
                p.email,
                g.license_number,
                g.experience_years
            FROM public.guides g
            JOIN public.participants p
                ON g.participant_id = p.participant_id
            ORDER BY p.first_name, p.last_name;
        """

        rows = fetch_all(query)

        for row in rows:
            participant_name = f"{row['first_name']} {row['last_name']}"

            self.tree.insert(
                "",
                "end",
                values=[
                    participant_name,
                    row["phone"],
                    row["email"],
                    row["license_number"],
                    row["experience_years"]
                ]
            )

    def clear_form(self):
        self.participant_var.set("")
        self.license_number_var.set("")
        self.experience_years_var.set("")

    def on_select(self, event):
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        guide_name = values[0]
        phone = values[1]

        participant_label = f"{guide_name} | {phone}"

        self.participant_var.set(participant_label)
        self.license_number_var.set(values[3])
        self.experience_years_var.set(values[4])

    def validate_form(self):
        if not self.participant_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Participant")
            return False

        if self.participant_var.get().strip() not in self.participant_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Participant מתוך הרשימה")
            return False

        if not self.license_number_var.get().strip():
            messagebox.showwarning("שגיאה", "יש למלא License Number")
            return False

        if not self.experience_years_var.get().strip():
            messagebox.showwarning("שגיאה", "יש למלא Experience Years")
            return False

        try:
            int(self.experience_years_var.get().strip())
        except ValueError:
            messagebox.showwarning("שגיאה", "Experience Years חייב להיות מספר שלם")
            return False

        return True

    def load_by_participant(self):
        if self.participant_var.get().strip() not in self.participant_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Participant מתוך הרשימה")
            return

        participant_id = self.participant_label_to_id[self.participant_var.get().strip()]

        # שאילתת SELECT לשליפת נתוני רישיון וניסיון של מדריך ספציפי לפי מזהה המשתתף שלו.
        query = """
            SELECT
                g.license_number,
                g.experience_years
            FROM public.guides g
            WHERE g.participant_id = %s;
        """

        row = fetch_one(query, (participant_id,))

        if row is None:
            messagebox.showinfo("לא נמצא", "המשתתף שנבחר אינו מוגדר כמדריך")
            return

        self.license_number_var.set(row["license_number"])
        self.experience_years_var.set(row["experience_years"])

    def add_guide(self):
        if not self.validate_form():
            return

        participant_id = self.participant_label_to_id[self.participant_var.get().strip()]
        license_number = self.license_number_var.get().strip()
        experience_years = int(self.experience_years_var.get().strip())

        # שאילתת INSERT להגדרת משתתף קיים כמדריך (הוספת רשומה לישות היורשת guides).
        query = """
            INSERT INTO public.guides
                (participant_id, license_number, experience_years)
            VALUES
                (%s, %s, %s);
        """

        success, message = execute_query(
            query,
            (participant_id, license_number, experience_years)
        )

        if success:
            messagebox.showinfo("הצלחה", "המדריך נוסף בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror(
                "שגיאה",
                "לא ניתן להוסיף את המדריך.\n"
                "יכול להיות שהמשתתף כבר מוגדר כמדריך או שיש בעיית נתונים.\n\n"
                f"{message}"
            )

    def update_guide(self):
        if not self.validate_form():
            return

        participant_id = self.participant_label_to_id[self.participant_var.get().strip()]
        license_number = self.license_number_var.get().strip()
        experience_years = int(self.experience_years_var.get().strip())

        # שאילתת UPDATE לעדכון מספר רישיון ושנות הניסיון של המדריך.
        query = """
            UPDATE public.guides
            SET
                license_number = %s,
                experience_years = %s
            WHERE participant_id = %s;
        """

        success, message = execute_query(
            query,
            (license_number, experience_years, participant_id)
        )

        if success:
            messagebox.showinfo("הצלחה", "המדריך עודכן בהצלחה")
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_guide(self):
        if self.participant_var.get().strip() not in self.participant_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Participant מתוך הרשימה")
            return

        confirm = messagebox.askyesno(
            "אישור מחיקה",
            "האם למחוק את הגדרת המשתתף כמדריך?\n"
            "המשתתף עצמו לא יימחק, רק הרשומה מטבלת guides."
        )

        if not confirm:
            return

        participant_id = self.participant_label_to_id[self.participant_var.get().strip()]

        # שאילתת DELETE להסרת רשומת מדריך מטבלת guides (המשתתף עצמו נשאר בטבלת participants).
        query = """
            DELETE FROM public.guides
            WHERE participant_id = %s;
        """

        success, message = execute_query(query, (participant_id,))

        if success:
            messagebox.showinfo("הצלחה", "המדריך נמחק בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)