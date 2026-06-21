# screens/participants_screen.py

import tkinter as tk
from tkinter import messagebox

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


class ParticipantsScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        # הגדרת משתני Tkinter (StringVar) המקושרים לשדות הקלט בטופס.
        # שינוי הערך במשתנה זה (באמצעות .set()) יעדכן מיידית את שדה הטקסט במסך,
        # וקריאה של הערך (באמצעות .get()) תשלוף את מה שהמשתמש הקליד בשדה.
        self.participant_id_var = tk.StringVar()
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.birth_date_var = tk.StringVar()

        self.tree = None

    def show(self):
        # ניקוי המסך הנוכחי לפני טעינת רכיבי המשתתפים
        self.app.clear_screen()

        create_title(self.root, "ניהול משתתפים")

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # בניית חלקי הממשק של המסך:
        self.create_form(main_frame)           # טופס להזנת פרטי משתתף
        self.create_actions(main_frame)        # כפתורי פעולות (הוספה, עדכון, מחיקה...)
        self.create_table_area(main_frame)     # טבלה המציגה את כלל הרשומות
        self.create_bottom_buttons()           # כפתורי ניווט תחתוניים (חזרה, רענון)

        # טעינה ראשונית של נתוני המשתתפים מה-DB אל הטבלה
        self.load_table()

    def create_form(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי משתתף",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=15,
            pady=15
        )
        form_frame.pack(fill="x", pady=10)

        fields = [
            ("Participant ID", self.participant_id_var),
            ("First Name", self.first_name_var),
            ("Last Name", self.last_name_var),
            ("Phone", self.phone_var),
            ("Email", self.email_var),
            ("Birth Date YYYY-MM-DD", self.birth_date_var),
        ]

        for index, (label_text, var) in enumerate(fields):
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

            entry = tk.Entry(
                form_frame,
                textvariable=var,
                width=25,
                font=("Arial", 10)
            )
            entry.grid(
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
            ("הוספה", self.add_participant, GREEN, 14),
            ("עדכון", self.update_participant, ORANGE, 14),
            ("מחיקה", self.delete_participant, RED, 14),
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
            "participant_id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "birth_date"
        ]

        headings = {
            "participant_id": "ID",
            "first_name": "First Name",
            "last_name": "Last Name",
            "phone": "Phone",
            "email": "Email",
            "birth_date": "Birth Date"
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
            self.load_table,
            color=GREEN,
            width=15
        )
        refresh_btn.pack(side="left", padx=10)

    def load_table(self):
        # ריקון הטבלה ב-UI מכל הרשומות הקיימות כדי למנוע כפילויות לפני הטעינה מחדש
        for item in self.tree.get_children():
            self.tree.delete(item)

        # שאילתת SELECT לשליפת כלל המשתתפים ממוינים לפי ה-ID שלהם
        query = """
            SELECT
                participant_id,
                first_name,
                last_name,
                phone,
                email,
                birth_date
            FROM public.participants
            ORDER BY participant_id;
        """

        # קריאה לפונקציית העזר מ-db.py שמבצעת את השאילתה ומחזירה רשימת מילונים
        rows = fetch_all(query)

        for row in rows:
            self.tree.insert(
                "",
                "end",
                values=[
                    row["participant_id"],
                    row["first_name"],
                    row["last_name"],
                    row["phone"],
                    row["email"],
                    row["birth_date"]
                ]
            )

    def clear_form(self):
        self.participant_id_var.set("")
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.birth_date_var.set("")

    def on_select(self, event):
        """
        פונקציה זו מופעלת אוטומטית (Event Binding) כאשר המשתמש בוחר שורה בטבלה.
        היא שולפת את ערכי השורה שנבחרה ומציבה אותם בתוך משתני ה-StringVar של הטופס,
        מה שמאפשר למשתמש לערוך או למחוק את הרשומה שנבחרה בקלות.
        """
        selected = self.tree.selection()

        if not selected:
            return

        # שליפת הערכים של השורה הראשונה שנבחרה
        values = self.tree.item(selected[0], "values")

        # עדכון משתני הטופס כדי שיציגו את הפרטים בשדות הקלט
        self.participant_id_var.set(values[0])
        self.first_name_var.set(values[1])
        self.last_name_var.set(values[2])
        self.phone_var.set(values[3])
        self.email_var.set(values[4])
        self.birth_date_var.set(values[5])

    def load_by_id(self):
        participant_id = self.participant_id_var.get().strip()

        if not participant_id:
            messagebox.showwarning("שגיאה", "יש להזין Participant ID")
            return

        query = """
            SELECT
                participant_id,
                first_name,
                last_name,
                phone,
                email,
                birth_date
            FROM public.participants
            WHERE participant_id = %s;
        """

        row = fetch_one(query, (participant_id,))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצא משתתף עם המזהה שהוזן")
            return

        self.first_name_var.set(row["first_name"])
        self.last_name_var.set(row["last_name"])
        self.phone_var.set(row["phone"])
        self.email_var.set(row["email"])
        self.birth_date_var.set(row["birth_date"])

    def add_participant(self):
        # קריאת נתוני הטופס וניקוי רווחים מיותרים בקצוות (strip)
        first_name = self.first_name_var.get().strip()
        last_name = self.last_name_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        birth_date = self.birth_date_var.get().strip()

        # ולידציה בסיסית: בדיקה שכל שדות החובה מולאו
        if not first_name or not last_name or not phone or not email or not birth_date:
            messagebox.showwarning("שגיאה", "יש למלא את כל השדות חוץ מ-ID")
            return

        # שאילתת INSERT מאובטחת. שימוש ב-%s מונע מתקפות SQL Injection באופן מובנה,
        # כיוון שהספרייה psycopg2 דואגת לבצע סניטציה וציטוט (quoting) מתאים לערכים.
        query = """
            INSERT INTO public.participants
                (first_name, last_name, phone, email, birth_date)
            VALUES
                (%s, %s, %s, %s, %s);
        """

        # ביצוע השאילתה מול ה-DB עם רשימת הערכים
        success, message = execute_query(
            query,
            (first_name, last_name, phone, email, birth_date)
        )

        if success:
            messagebox.showinfo("הצלחה", "המשתתף נוסף בהצלחה")
            self.clear_form() # ניקוי השדות לאחר ההוספה
            self.load_table() # טעינת הטבלה מחדש כדי להציג את המשתתף החדש
        else:
            messagebox.showerror("שגיאה", message)

    def update_participant(self):
        participant_id = self.participant_id_var.get().strip()
        first_name = self.first_name_var.get().strip()
        last_name = self.last_name_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        birth_date = self.birth_date_var.get().strip()

        if not participant_id:
            messagebox.showwarning("שגיאה", "לעדכון יש להזין Participant ID")
            return

        if not first_name or not last_name or not phone or not email or not birth_date:
            messagebox.showwarning("שגיאה", "יש למלא את כל השדות")
            return

        query = """
            UPDATE public.participants
            SET
                first_name = %s,
                last_name = %s,
                phone = %s,
                email = %s,
                birth_date = %s
            WHERE participant_id = %s;
        """

        success, message = execute_query(
            query,
            (first_name, last_name, phone, email, birth_date, participant_id)
        )

        if success:
            messagebox.showinfo("הצלחה", "המשתתף עודכן בהצלחה")
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_participant(self):
        participant_id = self.participant_id_var.get().strip()

        if not participant_id:
            messagebox.showwarning("שגיאה", "למחיקה יש להזין Participant ID")
            return

        confirm = messagebox.askyesno(
            "אישור מחיקה",
            "האם את בטוחה שברצונך למחוק את המשתתף?"
        )

        if not confirm:
            return

        query = """
            DELETE FROM public.participants
            WHERE participant_id = %s;
        """

        success, message = execute_query(query, (participant_id,))

        if success:
            messagebox.showinfo("הצלחה", "המשתתף נמחק בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)