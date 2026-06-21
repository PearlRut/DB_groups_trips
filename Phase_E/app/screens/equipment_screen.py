# screens/equipment_screen.py

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


class EquipmentScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        self.tree = None

        self.equipment_id_var = tk.StringVar()
        self.item_name_var = tk.StringVar()
        self.total_in_stock_var = tk.StringVar()
        self.supplier_var = tk.StringVar()

        self.supplier_name_to_id = {}

    def show(self):
        self.app.clear_screen()

        create_title(self.root, "ניהול ציוד")

        self.load_supplier_data()

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_form(main_frame)
        self.create_actions(main_frame)
        self.create_table_area(main_frame)
        self.create_bottom_buttons()

        self.load_table()

    def load_supplier_data(self):
        # מילון עזר למיפוי: שם החברה (מפתח) -> מזהה הספק הפיזי ב-DB (ערך).
        # מסייע להצגת שמות ספקים קריאים למשתמש בתיבת הבחירה (Combobox) בזמן שבשאילתות SQL אנו שולחים את המפתח הזר (ID).
        self.supplier_name_to_id = {}

        suppliers = fetch_all("""
            SELECT supplierid, company_name
            FROM public.supplier
            ORDER BY company_name;
        """)

        for row in suppliers:
            self.supplier_name_to_id[row["company_name"]] = row["supplierid"]

    def create_form(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי ציוד",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=15,
            pady=15
        )
        form_frame.pack(fill="x", pady=10)

        # רשימת השדות להצגה בטופס. שדה הספק מקבל כערכי בחירה (options) את רשימת השמות מהמילון שטענו קודם.
        fields = [
            ("Equipment ID", self.equipment_id_var, "entry", None),
            ("Item Name *", self.item_name_var, "entry", None),
            ("Total In Stock *", self.total_in_stock_var, "entry", None),
            ("Supplier *", self.supplier_var, "combo", list(self.supplier_name_to_id.keys())),
        ]

        for index, (label_text, var, widget_type, options) in enumerate(fields):
            label = tk.Label(
                form_frame,
                text=label_text,
                font=("Arial", 10),
                bg=BG_COLOR
            )
            label.grid(
                row=index // 2,
                column=(index % 2) * 2,
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
                    width=28,
                    font=("Arial", 10)
                )
            else:
                input_widget = tk.Entry(
                    form_frame,
                    textvariable=var,
                    width=30,
                    font=("Arial", 10)
                )

            input_widget.grid(
                row=index // 2,
                column=(index % 2) * 2 + 1,
                padx=8,
                pady=8
            )

    def create_actions(self, parent):
        actions_frame = tk.Frame(parent, bg=BG_COLOR)
        actions_frame.pack(fill="x", pady=10)

        buttons = [
            ("שליפה לפי ID", self.load_by_id, BLUE, 16),
            ("הוספה", self.add_equipment, GREEN, 14),
            ("עדכון", self.update_equipment, ORANGE, 14),
            ("מחיקה", self.delete_equipment, RED, 14),
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
            "equipmentid",
            "itemname",
            "totalinstock",
            "supplier_name"
        ]

        headings = {
            "equipmentid": "Equipment ID",
            "itemname": "Item Name",
            "totalinstock": "Total In Stock",
            "supplier_name": "Supplier"
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
        self.load_supplier_data()
        self.load_table()

    def load_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        # שאילתת SELECT לשליפת נתוני הציוד יחד עם שם החברה של הספק (company_name).
        # משתמשים ב-JOIN (חיבור) של טבלת הציוד (equipment) וטבלת הספקים (supplier) לפי מפתח זר (supplierid).
        query = """
            SELECT
                e.equipmentid,
                e.itemname,
                e.totalinstock,
                s.company_name AS supplier_name
            FROM public.equipment e
            JOIN public.supplier s
                ON e.supplierid = s.supplierid
            ORDER BY e.equipmentid;
        """

        rows = fetch_all(query)

        for row in rows:
            self.tree.insert(
                "",
                "end",
                values=[
                    row["equipmentid"],
                    row["itemname"],
                    row["totalinstock"],
                    row["supplier_name"]
                ]
            )

    def clear_form(self):
        self.equipment_id_var.set("")
        self.item_name_var.set("")
        self.total_in_stock_var.set("")
        self.supplier_var.set("")

    def on_select(self, event):
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")

        self.equipment_id_var.set(values[0])
        self.item_name_var.set(values[1])
        self.total_in_stock_var.set(values[2])
        self.supplier_var.set(values[3])

    def get_next_id(self):
        query = """
            SELECT COALESCE(MAX(equipmentid), 0) + 1 AS next_id
            FROM public.equipment;
        """

        row = fetch_one(query)

        if row is None:
            return 1

        return row["next_id"]

    def validate_form(self, require_id=False):
        if require_id and not self.equipment_id_var.get().strip():
            messagebox.showwarning("שגיאה", "יש להזין Equipment ID")
            return False

        if not self.item_name_var.get().strip():
            messagebox.showwarning("שגיאה", "יש למלא Item Name")
            return False

        if not self.total_in_stock_var.get().strip():
            messagebox.showwarning("שגיאה", "יש למלא Total In Stock")
            return False

        try:
            int(self.total_in_stock_var.get().strip())
        except ValueError:
            messagebox.showwarning("שגיאה", "Total In Stock חייב להיות מספר שלם")
            return False

        if not self.supplier_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Supplier")
            return False

        if self.supplier_var.get().strip() not in self.supplier_name_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Supplier מתוך הרשימה")
            return False

        return True

    def load_by_id(self):
        equipment_id = self.equipment_id_var.get().strip()

        if not equipment_id:
            messagebox.showwarning("שגיאה", "יש להזין Equipment ID")
            return

        # שאילתת SELECT לשליפת רשומת ציוד ספציפית לפי ה-ID שלה.
        # גם כאן מבצעים JOIN כדי לקבל את שם הספק במקום מזהה מספרי לא קריא.
        query = """
            SELECT
                e.equipmentid,
                e.itemname,
                e.totalinstock,
                s.company_name AS supplier_name
            FROM public.equipment e
            JOIN public.supplier s
                ON e.supplierid = s.supplierid
            WHERE e.equipmentid = %s;
        """

        row = fetch_one(query, (equipment_id,))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצא ציוד עם המזהה שהוזן")
            return

        self.equipment_id_var.set(row["equipmentid"])
        self.item_name_var.set(row["itemname"])
        self.total_in_stock_var.set(row["totalinstock"])
        self.supplier_var.set(row["supplier_name"])

    def add_equipment(self):
        if not self.validate_form(require_id=False):
            return

        equipment_id = self.equipment_id_var.get().strip()

        if equipment_id == "":
            equipment_id = self.get_next_id()

        item_name = self.item_name_var.get().strip()
        total_in_stock = int(self.total_in_stock_var.get().strip())
        supplier_id = self.supplier_name_to_id[self.supplier_var.get().strip()]

        # שאילתת INSERT להוספת פריט ציוד חדש לטבלת equipment.
        # הפרמטרים מועברים כסדרה של %s למניעת הזרקת SQL.
        query = """
            INSERT INTO public.equipment
                (equipmentid, itemname, totalinstock, supplierid)
            VALUES
                (%s, %s, %s, %s);
        """

        success, message = execute_query(
            query,
            (equipment_id, item_name, total_in_stock, supplier_id)
        )

        if success:
            messagebox.showinfo("הצלחה", "הציוד נוסף בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)

    def update_equipment(self):
        if not self.validate_form(require_id=True):
            return

        equipment_id = self.equipment_id_var.get().strip()
        item_name = self.item_name_var.get().strip()
        total_in_stock = int(self.total_in_stock_var.get().strip())
        supplier_id = self.supplier_name_to_id[self.supplier_var.get().strip()]

        # שאילתת UPDATE לעדכון שדות פריט הציוד לפי מפתח ראשי (equipmentid).
        # שימי לב: שינוי כמות הציוד במלאי (totalinstock) יפעיל באופן אוטומטי טריגר ב-Database
        # שיכתוב רשומה חדשה לטבלת הלוגים לצורך מעקב שינויים.
        query = """
            UPDATE public.equipment
            SET
                itemname = %s,
                totalinstock = %s,
                supplierid = %s
            WHERE equipmentid = %s;
        """

        success, message = execute_query(
            query,
            (item_name, total_in_stock, supplier_id, equipment_id)
        )

        if success:
            messagebox.showinfo(
                "הצלחה",
                "הציוד עודכן בהצלחה.\nאם שונתה הכמות במלאי, הטריגר יעדכן את טבלת הלוגים."
            )
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_equipment(self):
        equipment_id = self.equipment_id_var.get().strip()

        if not equipment_id:
            messagebox.showwarning("שגיאה", "למחיקה יש להזין Equipment ID")
            return

        confirm = messagebox.askyesno(
            "אישור מחיקה",
            "האם את בטוחה שברצונך למחוק את הציוד?\n"
            "מחיקה תתאפשר רק אם הציוד אינו משויך לטיולים."
        )

        if not confirm:
            return

        # שאילתת DELETE למחיקת פריט הציוד מבסיס הנתונים לפי ה-ID שלו.
        query = """
            DELETE FROM public.equipment
            WHERE equipmentid = %s;
        """

        success, message = execute_query(query, (equipment_id,))

        if success:
            messagebox.showinfo("הצלחה", "הציוד נמחק בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror(
                "לא ניתן למחוק",
                "לא ניתן למחוק את הציוד כי הוא כנראה משויך לרשומות אחרות במסד.\n"
                "זה תקין ושומר על שלמות הנתונים."
            )