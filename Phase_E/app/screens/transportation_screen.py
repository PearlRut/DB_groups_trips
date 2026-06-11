# screens/transportation_screen.py

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


class TransportationScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        self.tree = None

        self.transport_id_var = tk.StringVar()
        self.capacity_var = tk.StringVar()
        self.supplier_var = tk.StringVar()
        self.transport_type_var = tk.StringVar()

        self.supplier_name_to_id = {}
        self.transport_type_name_to_id = {}

    def show(self):
        self.app.clear_screen()

        create_title(self.root, "ניהול תחבורה")

        self.load_combo_data()

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_form(main_frame)
        self.create_actions(main_frame)
        self.create_table_area(main_frame)
        self.create_bottom_buttons()

        self.load_table()

    def load_combo_data(self):
        self.supplier_name_to_id = {}
        self.transport_type_name_to_id = {}

        suppliers = fetch_all("""
            SELECT supplierid, company_name
            FROM public.supplier
            ORDER BY company_name;
        """)

        for row in suppliers:
            self.supplier_name_to_id[row["company_name"]] = row["supplierid"]

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
            text="פרטי תחבורה",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=15,
            pady=15
        )
        form_frame.pack(fill="x", pady=10)

        fields = [
            ("Transport ID", self.transport_id_var, "entry", None),
            ("Capacity *", self.capacity_var, "entry", None),
            ("Supplier *", self.supplier_var, "combo", list(self.supplier_name_to_id.keys())),
            ("Transport Type *", self.transport_type_var, "combo", list(self.transport_type_name_to_id.keys())),
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
                    width=30,
                    font=("Arial", 10)
                )
            else:
                input_widget = tk.Entry(
                    form_frame,
                    textvariable=var,
                    width=32,
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
            ("הוספה", self.add_transportation, GREEN, 14),
            ("עדכון", self.update_transportation, ORANGE, 14),
            ("מחיקה", self.delete_transportation, RED, 14),
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
            "transportid",
            "capacity",
            "supplier_name",
            "transport_type_name"
        ]

        headings = {
            "transportid": "Transport ID",
            "capacity": "Capacity",
            "supplier_name": "Supplier",
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
                tr.transportid,
                tr.capacity,
                s.company_name AS supplier_name,
                tt.transport_type_name
            FROM public.transportation tr
            JOIN public.supplier s
                ON tr.supplierid = s.supplierid
            JOIN public.transport_types tt
                ON tr.transport_type_id = tt.transport_type_id
            ORDER BY tr.transportid;
        """

        rows = fetch_all(query)

        for row in rows:
            self.tree.insert(
                "",
                "end",
                values=[
                    row["transportid"],
                    row["capacity"],
                    row["supplier_name"],
                    row["transport_type_name"]
                ]
            )

    def clear_form(self):
        self.transport_id_var.set("")
        self.capacity_var.set("")
        self.supplier_var.set("")
        self.transport_type_var.set("")

    def on_select(self, event):
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")

        self.transport_id_var.set(values[0])
        self.capacity_var.set(values[1])
        self.supplier_var.set(values[2])
        self.transport_type_var.set(values[3])

    def get_next_id(self):
        query = """
            SELECT COALESCE(MAX(transportid), 0) + 1 AS next_id
            FROM public.transportation;
        """

        row = fetch_one(query)

        if row is None:
            return 1

        return row["next_id"]

    def validate_form(self, require_id=False):
        if require_id and not self.transport_id_var.get().strip():
            messagebox.showwarning("שגיאה", "יש להזין Transport ID")
            return False

        if not self.capacity_var.get().strip():
            messagebox.showwarning("שגיאה", "יש למלא Capacity")
            return False

        try:
            int(self.capacity_var.get().strip())
        except ValueError:
            messagebox.showwarning("שגיאה", "Capacity חייב להיות מספר שלם")
            return False

        if not self.supplier_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Supplier")
            return False

        if self.supplier_var.get().strip() not in self.supplier_name_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Supplier מתוך הרשימה")
            return False

        if not self.transport_type_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Transport Type")
            return False

        if self.transport_type_var.get().strip() not in self.transport_type_name_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Transport Type מתוך הרשימה")
            return False

        return True

    def load_by_id(self):
        transport_id = self.transport_id_var.get().strip()

        if not transport_id:
            messagebox.showwarning("שגיאה", "יש להזין Transport ID")
            return

        query = """
            SELECT
                tr.transportid,
                tr.capacity,
                s.company_name AS supplier_name,
                tt.transport_type_name
            FROM public.transportation tr
            JOIN public.supplier s
                ON tr.supplierid = s.supplierid
            JOIN public.transport_types tt
                ON tr.transport_type_id = tt.transport_type_id
            WHERE tr.transportid = %s;
        """

        row = fetch_one(query, (transport_id,))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצאה תחבורה עם המזהה שהוזן")
            return

        self.transport_id_var.set(row["transportid"])
        self.capacity_var.set(row["capacity"])
        self.supplier_var.set(row["supplier_name"])
        self.transport_type_var.set(row["transport_type_name"])

    def add_transportation(self):
        if not self.validate_form(require_id=False):
            return

        transport_id = self.transport_id_var.get().strip()

        if transport_id == "":
            transport_id = self.get_next_id()

        capacity = int(self.capacity_var.get().strip())
        supplier_id = self.supplier_name_to_id[self.supplier_var.get().strip()]
        transport_type_id = self.transport_type_name_to_id[self.transport_type_var.get().strip()]

        query = """
            INSERT INTO public.transportation
                (transportid, capacity, supplierid, transport_type_id)
            VALUES
                (%s, %s, %s, %s);
        """

        success, message = execute_query(
            query,
            (transport_id, capacity, supplier_id, transport_type_id)
        )

        if success:
            messagebox.showinfo("הצלחה", "התחבורה נוספה בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)

    def update_transportation(self):
        if not self.validate_form(require_id=True):
            return

        transport_id = self.transport_id_var.get().strip()
        capacity = int(self.capacity_var.get().strip())
        supplier_id = self.supplier_name_to_id[self.supplier_var.get().strip()]
        transport_type_id = self.transport_type_name_to_id[self.transport_type_var.get().strip()]

        query = """
            UPDATE public.transportation
            SET
                capacity = %s,
                supplierid = %s,
                transport_type_id = %s
            WHERE transportid = %s;
        """

        success, message = execute_query(
            query,
            (capacity, supplier_id, transport_type_id, transport_id)
        )

        if success:
            messagebox.showinfo("הצלחה", "התחבורה עודכנה בהצלחה")
            self.load_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_transportation(self):
        transport_id = self.transport_id_var.get().strip()

        if not transport_id:
            messagebox.showwarning("שגיאה", "למחיקה יש להזין Transport ID")
            return

        confirm = messagebox.askyesno(
            "אישור מחיקה",
            "האם את בטוחה שברצונך למחוק את התחבורה?\n"
            "מחיקה תתאפשר רק אם התחבורה אינה משויכת לטיולים."
        )

        if not confirm:
            return

        query = """
            DELETE FROM public.transportation
            WHERE transportid = %s;
        """

        success, message = execute_query(query, (transport_id,))

        if success:
            messagebox.showinfo("הצלחה", "התחבורה נמחקה בהצלחה")
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror(
                "לא ניתן למחוק",
                "לא ניתן למחוק את התחבורה כי היא כנראה משויכת לרשומות אחרות במסד.\n"
                "זה תקין ושומר על שלמות הנתונים."
            )