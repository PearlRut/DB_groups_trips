# screens/simple_crud_screen.py

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


class SimpleCrudScreen:
    def __init__(self, root, app, config):
        self.root = root
        self.app = app

        # פירוק הגדרות הטבלה שהועברו מה-AppController
        self.title = config["title"]               # כותרת המסך (למשל: "ניהול מסלולים")
        self.table_name = config["table_name"]     # שם הטבלה הפיזית בבסיס הנתונים (למשל: "routes")
        self.primary_key = config["primary_key"]   # שם עמודת המפתח הראשי (למשל: "route_id")
        self.fields = config["fields"]             # רשימת העמודות, סוגי הפקדים, והאפשרויות שלהן

        # מילון לשמירת משתני ה-StringVar של Tkinter בצורה דינמית לפי שמות העמודות
        self.vars = {}
        self.tree = None

    def show(self):
        self.app.clear_screen()

        create_title(self.root, self.title)

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_form(main_frame)
        self.create_actions(main_frame)
        self.create_records_table(main_frame)
        self.create_bottom_buttons()

        self.load_table()

    def create_form(self, parent):
        # יצירת מסגרת טופס מעוצבת
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי רשומה",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=15,
            pady=15
        )
        form_frame.pack(fill="x", pady=10)

        # מעבר בלולאה על כל השדות שהוגדרו עבור הטבלה ויצירה דינמית שלהם בממשק
        for index, field in enumerate(self.fields):
            column_name, label_text, required, widget_type, options = field

            # יצירת StringVar ושמירתו במילון תחת שם העמודה ב-SQL
            var = tk.StringVar()
            self.vars[column_name] = var

            # סימון כוכבית ליד שדות חובה (שאינם המפתח הראשי שמיוצר אוטומטית)
            required_mark = " *" if required and column_name != self.primary_key else ""

            label = tk.Label(
                form_frame,
                text=label_text + required_mark,
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

            if widget_type == "combo":
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
            ("שליפה לפי ID", self.load_record_by_id, BLUE, 16),
            ("הוספה", self.add_record, GREEN, 14),
            ("עדכון", self.update_record, ORANGE, 14),
            ("מחיקה", self.delete_record, RED, 14),
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

    def create_records_table(self, parent):
        table_frame = tk.Frame(parent, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, pady=10)

        columns = [field[0] for field in self.fields]
        headings = {field[0]: field[1] for field in self.fields}

        self.tree = create_table(table_frame, columns, headings)
        self.tree.bind("<<TreeviewSelect>>", self.on_record_select)

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
            self.load_table,
            color=GREEN,
            width=15
        )
        refresh_btn.pack(side="left", padx=10)

    def load_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        columns = [field[0] for field in self.fields]
        columns_sql = ", ".join(columns)

        query = f"""
            SELECT {columns_sql}
            FROM public.{self.table_name}
            ORDER BY {self.primary_key};
        """

        rows = fetch_all(query)

        for row in rows:
            self.tree.insert(
                "",
                "end",
                values=[
                    "" if row[column] is None else row[column]
                    for column in columns
                ]
            )

    def clear_form(self):
        for var in self.vars.values():
            var.set("")

    def on_record_select(self, event):
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        columns = [field[0] for field in self.fields]

        for index, column_name in enumerate(columns):
            self.vars[column_name].set(values[index])

    def load_record_by_id(self):
        record_id = self.vars[self.primary_key].get().strip()

        if not record_id:
            messagebox.showwarning("שגיאה", "יש להזין ID")
            return

        columns = [field[0] for field in self.fields]
        columns_sql = ", ".join(columns)

        query = f"""
            SELECT {columns_sql}
            FROM public.{self.table_name}
            WHERE {self.primary_key} = %s;
        """

        row = fetch_one(query, (record_id,))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצאה רשומה עם המזהה שהוזן")
            return

        for column in columns:
            value = "" if row[column] is None else row[column]
            self.vars[column].set(value)

    def get_next_id(self):
        # מציאת המזהה הבא פנוי בטבלה. מתבצע על ידי שליפת הערך המקסימלי הקיים והוספת 1.
        # COALESCE מטפל במצב שבו הטבלה ריקה לחלוטין (ואז MAX מחזיר NULL) ומחזיר במקומו 0.
        query = f"""
            SELECT COALESCE(MAX({self.primary_key}), 0) + 1 AS next_id
            FROM public.{self.table_name};
        """

        row = fetch_one(query)

        if row is None:
            return 1

        return row["next_id"]

    def get_form_values_for_insert(self):
        # איסוף השמות והערכים עבור שאילתת INSERT
        columns = []
        values = []

        record_id = self.vars[self.primary_key].get().strip()

        # אם המשתמש לא הזין מזהה, המערכת מייצרת מזהה חדש אוטומטית על ידי get_next_id()
        if record_id == "":
            record_id = self.get_next_id()

        columns.append(self.primary_key)
        values.append(record_id)

        for column_name, label_text, required, widget_type, options in self.fields:
            if column_name == self.primary_key:
                continue

            value = self.vars[column_name].get().strip()

            # בדיקת תקינות: שדה חובה אינו יכול להיות ריק
            if required and value == "":
                messagebox.showwarning(
                    "שגיאה",
                    f"יש למלא את השדה: {label_text}"
                )
                return None, None

            # המרת מחרוזת ריקה ל-None כדי שיוזן ערך NULL ב-Database
            if value == "":
                value = None

            columns.append(column_name)
            values.append(value)

        return columns, values

    def get_form_values_for_update(self):
        # איסוף השמות והערכים עבור שאילתת UPDATE (לא כולל את המפתח הראשי שישמש לסינון ב-WHERE)
        columns = []
        values = []

        for column_name, label_text, required, widget_type, options in self.fields:
            if column_name == self.primary_key:
                continue

            value = self.vars[column_name].get().strip()

            if required and value == "":
                messagebox.showwarning(
                    "שגיאה",
                    f"יש למלא את השדה: {label_text}"
                )
                return None, None

            if value == "":
                value = None

            columns.append(column_name)
            values.append(value)

        return columns, values

    def add_record(self):
        columns, values = self.get_form_values_for_insert()

        if columns is None:
            return

        columns_sql = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))

        query = f"""
            INSERT INTO public.{self.table_name}
                ({columns_sql})
            VALUES
                ({placeholders});
        """

        success, message = execute_query(query, values)

        if success:
            messagebox.showinfo("הצלחה", "הרשומה נוספה בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)

    def update_record(self):
        record_id = self.vars[self.primary_key].get().strip()

        if not record_id:
            messagebox.showwarning("שגיאה", "לעדכון יש להזין ID")
            return

        columns, values = self.get_form_values_for_update()

        if columns is None:
            return

        set_clause = ", ".join([f"{column} = %s" for column in columns])

        query = f"""
            UPDATE public.{self.table_name}
            SET {set_clause}
            WHERE {self.primary_key} = %s;
        """

        values.append(record_id)

        success, message = execute_query(query, values)

        if success:
            messagebox.showinfo("הצלחה", "הרשומה עודכנה בהצלחה")
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_record(self):
        record_id = self.vars[self.primary_key].get().strip()

        if not record_id:
            messagebox.showwarning("שגיאה", "למחיקה יש להזין ID")
            return

        confirm = messagebox.askyesno(
            "אישור מחיקה",
            "האם את בטוחה שברצונך למחוק את הרשומה?"
        )

        if not confirm:
            return

        query = f"""
            DELETE FROM public.{self.table_name}
            WHERE {self.primary_key} = %s;
        """

        success, message = execute_query(query, (record_id,))

        if success:
            messagebox.showinfo("הצלחה", "הרשומה נמחקה בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)