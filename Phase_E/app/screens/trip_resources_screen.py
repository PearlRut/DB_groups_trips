# screens/trip_resources_screen.py

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


class TripResourcesScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        self.trip_label_to_id = {}
        self.trip_id_to_label = {}

        self.location_label_to_id = {}
        self.location_id_to_label = {}

        self.equipment_label_to_id = {}
        self.equipment_id_to_label = {}

        self.transport_label_to_id = {}
        self.transport_id_to_label = {}

        self.location_tree = None
        self.equipment_tree = None
        self.transport_tree = None

        self.location_trip_combo = None
        self.location_location_combo = None

        self.equipment_trip_combo = None
        self.equipment_equipment_combo = None

        self.transport_trip_combo = None
        self.transport_transport_combo = None

        # location_trip
        self.location_trip_var = tk.StringVar()
        self.location_order_var = tk.StringVar()
        self.location_location_var = tk.StringVar()

        # trip_equipment
        self.equipment_trip_var = tk.StringVar()
        self.equipment_item_var = tk.StringVar()
        self.quantity_allocated_var = tk.StringVar()
        self.checkout_date_var = tk.StringVar()
        self.return_date_var = tk.StringVar()

        self.selected_equipment_old_trip_id = None
        self.selected_equipment_old_equipment_id = None

        # trip_transportation
        self.transport_trip_var = tk.StringVar()
        self.transport_item_var = tk.StringVar()
        self.departure_date_time_var = tk.StringVar()
        self.arrival_date_time_var = tk.StringVar()

        self.selected_transport_old_trip_id = None
        self.selected_transport_old_transport_id = None
        self.selected_transport_old_departure = None

    def show(self):
        self.app.clear_screen()

        create_title(self.root, "ניהול משאבי טיול")

        self.load_reference_data()

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        location_tab = tk.Frame(notebook, bg=BG_COLOR)
        equipment_tab = tk.Frame(notebook, bg=BG_COLOR)
        transport_tab = tk.Frame(notebook, bg=BG_COLOR)

        notebook.add(location_tab, text="מיקומים בטיול")
        notebook.add(equipment_tab, text="ציוד לטיול")
        notebook.add(transport_tab, text="תחבורה לטיול")

        self.create_location_tab(location_tab)
        self.create_equipment_tab(equipment_tab)
        self.create_transport_tab(transport_tab)

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

        self.load_location_table()
        self.load_equipment_table()
        self.load_transport_table()

    def make_unique_label(self, mapping, base_label):
        label = base_label
        counter = 2

        while label in mapping:
            label = f"{base_label} ({counter})"
            counter += 1

        return label

    def load_reference_data(self):
        self.trip_label_to_id = {}
        self.trip_id_to_label = {}

        self.location_label_to_id = {}
        self.location_id_to_label = {}

        self.equipment_label_to_id = {}
        self.equipment_id_to_label = {}

        self.transport_label_to_id = {}
        self.transport_id_to_label = {}

        trips = fetch_all("""
            SELECT trip_id, trip_name, start_date
            FROM public.trips
            ORDER BY trip_name, start_date;
        """)

        for row in trips:
            base_label = f"{row['trip_name']} | {row['start_date']}"
            label = self.make_unique_label(self.trip_label_to_id, base_label)

            self.trip_label_to_id[label] = row["trip_id"]
            self.trip_id_to_label[row["trip_id"]] = label

        locations = fetch_all("""
            SELECT locationid, locationname, region, address
            FROM public.location
            ORDER BY locationname, region;
        """)

        for row in locations:
            base_label = f"{row['locationname']} | {row['region']} | {row['address']}"
            label = self.make_unique_label(self.location_label_to_id, base_label)

            self.location_label_to_id[label] = row["locationid"]
            self.location_id_to_label[row["locationid"]] = label

        equipment = fetch_all("""
            SELECT
                e.equipmentid,
                e.itemname,
                e.totalinstock,
                s.company_name AS supplier_name
            FROM public.equipment e
            JOIN public.supplier s
                ON e.supplierid = s.supplierid
            ORDER BY e.itemname, s.company_name;
        """)

        for row in equipment:
            base_label = f"{row['itemname']} | מלאי: {row['totalinstock']} | {row['supplier_name']}"
            label = self.make_unique_label(self.equipment_label_to_id, base_label)

            self.equipment_label_to_id[label] = row["equipmentid"]
            self.equipment_id_to_label[row["equipmentid"]] = label

        transports = fetch_all("""
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
            ORDER BY tt.transport_type_name, tr.capacity, s.company_name;
        """)

        for row in transports:
            base_label = f"{row['transport_type_name']} | מקומות: {row['capacity']} | {row['supplier_name']}"
            label = self.make_unique_label(self.transport_label_to_id, base_label)

            self.transport_label_to_id[label] = row["transportid"]
            self.transport_id_to_label[row["transportid"]] = label

    def refresh_all(self):
        self.load_reference_data()

        if self.location_trip_combo is not None:
            self.location_trip_combo["values"] = list(self.trip_label_to_id.keys())

        if self.location_location_combo is not None:
            self.location_location_combo["values"] = list(self.location_label_to_id.keys())

        if self.equipment_trip_combo is not None:
            self.equipment_trip_combo["values"] = list(self.trip_label_to_id.keys())

        if self.equipment_equipment_combo is not None:
            self.equipment_equipment_combo["values"] = list(self.equipment_label_to_id.keys())

        if self.transport_trip_combo is not None:
            self.transport_trip_combo["values"] = list(self.trip_label_to_id.keys())

        if self.transport_transport_combo is not None:
            self.transport_transport_combo["values"] = list(self.transport_label_to_id.keys())

        self.load_location_table()
        self.load_equipment_table()
        self.load_transport_table()

    # ---------------------------------------------------
    # location_trip tab
    # ---------------------------------------------------
    def create_location_tab(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי מיקום בטיול",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=12,
            pady=12
        )
        form_frame.pack(fill="x", padx=10, pady=8)

        fields = [
            ("Trip *", self.location_trip_var, "combo", list(self.trip_label_to_id.keys())),
            ("Location Order *", self.location_order_var, "entry", None),
            ("Location *", self.location_location_var, "combo", list(self.location_label_to_id.keys())),
        ]

        for index, (label_text, var, widget_type, options) in enumerate(fields):
            label = tk.Label(form_frame, text=label_text, font=("Arial", 10), bg=BG_COLOR)
            label.grid(row=0, column=index * 2, padx=8, pady=8, sticky="w")

            if widget_type == "combo":
                widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="readonly",
                    width=38,
                    font=("Arial", 10)
                )

                if label_text.startswith("Trip"):
                    self.location_trip_combo = widget
                else:
                    self.location_location_combo = widget
            else:
                widget = tk.Entry(
                    form_frame,
                    textvariable=var,
                    width=20,
                    font=("Arial", 10)
                )

            widget.grid(row=0, column=index * 2 + 1, padx=8, pady=8)

        actions_frame = tk.Frame(parent, bg=BG_COLOR)
        actions_frame.pack(fill="x", padx=10, pady=5)

        buttons = [
            ("שליפה לפי Trip + Order", self.load_location_by_key, BLUE, 22),
            ("הוספה", self.add_location_trip, GREEN, 12),
            ("עדכון", self.update_location_trip, ORANGE, 12),
            ("מחיקה", self.delete_location_trip, RED, 12),
            ("ניקוי שדות", self.clear_location_form, GRAY, 14),
        ]

        for text, command, color, width in buttons:
            btn = create_button(actions_frame, text, command, color=color, width=width)
            btn.pack(side="left", padx=5)

        table_frame = tk.Frame(parent, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = [
            "trip_name",
            "trip_start_date",
            "location_order",
            "location_name",
            "region",
            "address"
        ]

        headings = {
            "trip_name": "Trip",
            "trip_start_date": "Trip Start",
            "location_order": "Order",
            "location_name": "Location",
            "region": "Region",
            "address": "Address"
        }

        self.location_tree = create_table(table_frame, columns, headings)
        self.location_tree.bind("<<TreeviewSelect>>", self.on_location_select)

    def load_location_table(self):
        if self.location_tree is None:
            return

        for item in self.location_tree.get_children():
            self.location_tree.delete(item)

        rows = fetch_all("""
            SELECT
                lt.trip_id,
                lt.location_order,
                l.locationid,
                t.trip_name,
                t.start_date,
                l.locationname,
                l.region,
                l.address
            FROM public.location_trip lt
            JOIN public.trips t
                ON lt.trip_id = t.trip_id
            JOIN public.location l
                ON lt.locationid = l.locationid
            ORDER BY lt.trip_id, lt.location_order;
        """)

        for row in rows:
            item_id = f"location|{row['trip_id']}|{row['location_order']}"

            self.location_tree.insert(
                "",
                "end",
                iid=item_id,
                values=[
                    row["trip_name"],
                    row["start_date"],
                    row["location_order"],
                    row["locationname"],
                    row["region"],
                    row["address"]
                ]
            )

    def clear_location_form(self):
        self.location_trip_var.set("")
        self.location_order_var.set("")
        self.location_location_var.set("")

    def validate_location_form(self, require_location=True):
        if not self.location_trip_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Trip")
            return False

        if self.location_trip_var.get().strip() not in self.trip_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Trip מתוך הרשימה")
            return False

        if not self.location_order_var.get().strip():
            messagebox.showwarning("שגיאה", "יש להזין Location Order")
            return False

        try:
            int(self.location_order_var.get().strip())
        except ValueError:
            messagebox.showwarning("שגיאה", "Location Order חייב להיות מספר שלם")
            return False

        if require_location:
            if not self.location_location_var.get().strip():
                messagebox.showwarning("שגיאה", "יש לבחור Location")
                return False

            if self.location_location_var.get().strip() not in self.location_label_to_id:
                messagebox.showwarning("שגיאה", "יש לבחור Location מתוך הרשימה")
                return False

        return True

    def on_location_select(self, event):
        selected = self.location_tree.selection()

        if not selected:
            return

        item_id = selected[0]

        try:
            _, trip_id_text, location_order_text = item_id.split("|")
            trip_id = int(trip_id_text)
            location_order = int(location_order_text)
        except ValueError:
            messagebox.showerror("שגיאה", "לא ניתן לקרוא את המיקום שנבחר")
            return

        row = fetch_one("""
            SELECT trip_id, location_order, locationid
            FROM public.location_trip
            WHERE trip_id = %s
              AND location_order = %s;
        """, (trip_id, location_order))

        if row is None:
            return

        self.location_trip_var.set(self.trip_id_to_label.get(row["trip_id"], ""))
        self.location_order_var.set(row["location_order"])
        self.location_location_var.set(self.location_id_to_label.get(row["locationid"], ""))

    def load_location_by_key(self):
        if not self.validate_location_form(require_location=False):
            return

        trip_id = self.trip_label_to_id[self.location_trip_var.get().strip()]
        location_order = int(self.location_order_var.get().strip())

        row = fetch_one("""
            SELECT trip_id, location_order, locationid
            FROM public.location_trip
            WHERE trip_id = %s
              AND location_order = %s;
        """, (trip_id, location_order))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצא מיקום בטיול לפי המפתח שהוזן")
            return

        self.location_trip_var.set(self.trip_id_to_label.get(row["trip_id"], ""))
        self.location_order_var.set(row["location_order"])
        self.location_location_var.set(self.location_id_to_label.get(row["locationid"], ""))

    def add_location_trip(self):
        if not self.validate_location_form(require_location=True):
            return

        trip_id = self.trip_label_to_id[self.location_trip_var.get().strip()]
        location_order = int(self.location_order_var.get().strip())
        location_id = self.location_label_to_id[self.location_location_var.get().strip()]

        query = """
            INSERT INTO public.location_trip
                (location_order, trip_id, locationid)
            VALUES
                (%s, %s, %s);
        """

        success, message = execute_query(query, (location_order, trip_id, location_id))

        if success:
            messagebox.showinfo("הצלחה", "המיקום נוסף לטיול בהצלחה")
            self.clear_location_form()
            self.load_location_table()
        else:
            messagebox.showerror("שגיאה", message)

    def update_location_trip(self):
        if not self.validate_location_form(require_location=True):
            return

        trip_id = self.trip_label_to_id[self.location_trip_var.get().strip()]
        location_order = int(self.location_order_var.get().strip())
        location_id = self.location_label_to_id[self.location_location_var.get().strip()]

        query = """
            UPDATE public.location_trip
            SET locationid = %s
            WHERE trip_id = %s
              AND location_order = %s;
        """

        success, message = execute_query(query, (location_id, trip_id, location_order))

        if success:
            messagebox.showinfo("הצלחה", "המיקום בטיול עודכן בהצלחה")
            self.load_location_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_location_trip(self):
        if not self.validate_location_form(require_location=False):
            return

        confirm = messagebox.askyesno("אישור מחיקה", "האם למחוק את המיקום מהטיול?")

        if not confirm:
            return

        trip_id = self.trip_label_to_id[self.location_trip_var.get().strip()]
        location_order = int(self.location_order_var.get().strip())

        query = """
            DELETE FROM public.location_trip
            WHERE trip_id = %s
              AND location_order = %s;
        """

        success, message = execute_query(query, (trip_id, location_order))

        if success:
            messagebox.showinfo("הצלחה", "המיקום נמחק מהטיול בהצלחה")
            self.clear_location_form()
            self.load_location_table()
        else:
            messagebox.showerror("שגיאה", message)

    # ---------------------------------------------------
    # trip_equipment tab
    # ---------------------------------------------------
    def create_equipment_tab(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי ציוד לטיול",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=12,
            pady=12
        )
        form_frame.pack(fill="x", padx=10, pady=8)

        fields = [
            ("Trip *", self.equipment_trip_var, "combo", list(self.trip_label_to_id.keys())),
            ("Equipment *", self.equipment_item_var, "combo", list(self.equipment_label_to_id.keys())),
            ("Quantity Allocated *", self.quantity_allocated_var, "entry", None),
            ("Checkout Date YYYY-MM-DD *", self.checkout_date_var, "entry", None),
            ("Return Date YYYY-MM-DD", self.return_date_var, "entry", None),
        ]

        for index, (label_text, var, widget_type, options) in enumerate(fields):
            label = tk.Label(form_frame, text=label_text, font=("Arial", 10), bg=BG_COLOR)
            label.grid(row=index // 3, column=(index % 3) * 2, padx=8, pady=8, sticky="w")

            if widget_type == "combo":
                widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="readonly",
                    width=38,
                    font=("Arial", 10)
                )

                if label_text.startswith("Trip"):
                    self.equipment_trip_combo = widget
                else:
                    self.equipment_equipment_combo = widget
            else:
                widget = tk.Entry(
                    form_frame,
                    textvariable=var,
                    width=24,
                    font=("Arial", 10)
                )

            widget.grid(row=index // 3, column=(index % 3) * 2 + 1, padx=8, pady=8)

        actions_frame = tk.Frame(parent, bg=BG_COLOR)
        actions_frame.pack(fill="x", padx=10, pady=5)

        buttons = [
            ("שליפה לפי Trip + Equipment", self.load_equipment_by_key, BLUE, 26),
            ("הוספה", self.add_trip_equipment, GREEN, 12),
            ("עדכון", self.update_trip_equipment, ORANGE, 12),
            ("מחיקה", self.delete_trip_equipment, RED, 12),
            ("ניקוי שדות", self.clear_equipment_form, GRAY, 14),
        ]

        for text, command, color, width in buttons:
            btn = create_button(actions_frame, text, command, color=color, width=width)
            btn.pack(side="left", padx=5)

        table_frame = tk.Frame(parent, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = [
            "trip_name",
            "equipment_name",
            "quantityallocated",
            "checkout_date",
            "return_date",
            "supplier_name"
        ]

        headings = {
            "trip_name": "Trip",
            "equipment_name": "Equipment",
            "quantityallocated": "Quantity",
            "checkout_date": "Checkout Date",
            "return_date": "Return Date",
            "supplier_name": "Supplier"
        }

        self.equipment_tree = create_table(table_frame, columns, headings)
        self.equipment_tree.bind("<<TreeviewSelect>>", self.on_equipment_select)

    def load_equipment_table(self):
        if self.equipment_tree is None:
            return

        for item in self.equipment_tree.get_children():
            self.equipment_tree.delete(item)

        rows = fetch_all("""
            SELECT
                te.trip_id,
                te.equipmentid,
                te.quantityallocated,
                te.checkout_date,
                te.return_date,
                t.trip_name,
                e.itemname,
                s.company_name AS supplier_name
            FROM public.trip_equipment te
            JOIN public.trips t
                ON te.trip_id = t.trip_id
            JOIN public.equipment e
                ON te.equipmentid = e.equipmentid
            JOIN public.supplier s
                ON e.supplierid = s.supplierid
            ORDER BY te.trip_id, e.itemname;
        """)

        for row in rows:
            item_id = f"equipment|{row['trip_id']}|{row['equipmentid']}"

            self.equipment_tree.insert(
                "",
                "end",
                iid=item_id,
                values=[
                    row["trip_name"],
                    row["itemname"],
                    row["quantityallocated"],
                    row["checkout_date"],
                    "" if row["return_date"] is None else row["return_date"],
                    row["supplier_name"]
                ]
            )

    def clear_equipment_form(self):
        self.equipment_trip_var.set("")
        self.equipment_item_var.set("")
        self.quantity_allocated_var.set("")
        self.checkout_date_var.set("")
        self.return_date_var.set("")
        self.selected_equipment_old_trip_id = None
        self.selected_equipment_old_equipment_id = None

    def validate_equipment_form(self, require_details=True):
        if not self.equipment_trip_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Trip")
            return False

        if self.equipment_trip_var.get().strip() not in self.trip_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Trip מתוך הרשימה")
            return False

        if not self.equipment_item_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Equipment")
            return False

        if self.equipment_item_var.get().strip() not in self.equipment_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Equipment מתוך הרשימה")
            return False

        if require_details:
            if not self.quantity_allocated_var.get().strip():
                messagebox.showwarning("שגיאה", "יש להזין Quantity Allocated")
                return False

            try:
                int(self.quantity_allocated_var.get().strip())
            except ValueError:
                messagebox.showwarning("שגיאה", "Quantity Allocated חייב להיות מספר שלם")
                return False

            if not self.checkout_date_var.get().strip():
                messagebox.showwarning("שגיאה", "יש להזין Checkout Date")
                return False

        return True

    def on_equipment_select(self, event):
        selected = self.equipment_tree.selection()

        if not selected:
            return

        item_id = selected[0]

        try:
            _, trip_id_text, equipment_id_text = item_id.split("|")
            trip_id = int(trip_id_text)
            equipment_id = int(equipment_id_text)
        except ValueError:
            messagebox.showerror("שגיאה", "לא ניתן לקרוא את הציוד שנבחר")
            return

        row = fetch_one("""
            SELECT
                trip_id,
                equipmentid,
                quantityallocated,
                checkout_date,
                return_date
            FROM public.trip_equipment
            WHERE trip_id = %s
              AND equipmentid = %s;
        """, (trip_id, equipment_id))

        if row is None:
            return

        self.selected_equipment_old_trip_id = row["trip_id"]
        self.selected_equipment_old_equipment_id = row["equipmentid"]

        self.equipment_trip_var.set(self.trip_id_to_label.get(row["trip_id"], ""))
        self.equipment_item_var.set(self.equipment_id_to_label.get(row["equipmentid"], ""))
        self.quantity_allocated_var.set(row["quantityallocated"])
        self.checkout_date_var.set(row["checkout_date"])
        self.return_date_var.set("" if row["return_date"] is None else row["return_date"])

    def load_equipment_by_key(self):
        if not self.validate_equipment_form(require_details=False):
            return

        trip_id = self.trip_label_to_id[self.equipment_trip_var.get().strip()]
        equipment_id = self.equipment_label_to_id[self.equipment_item_var.get().strip()]

        row = fetch_one("""
            SELECT
                trip_id,
                equipmentid,
                quantityallocated,
                checkout_date,
                return_date
            FROM public.trip_equipment
            WHERE trip_id = %s
              AND equipmentid = %s;
        """, (trip_id, equipment_id))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצא ציוד לטיול לפי המפתח שהוזן")
            return

        self.selected_equipment_old_trip_id = row["trip_id"]
        self.selected_equipment_old_equipment_id = row["equipmentid"]

        self.quantity_allocated_var.set(row["quantityallocated"])
        self.checkout_date_var.set(row["checkout_date"])
        self.return_date_var.set("" if row["return_date"] is None else row["return_date"])

    def add_trip_equipment(self):
        if not self.validate_equipment_form(require_details=True):
            return

        trip_id = self.trip_label_to_id[self.equipment_trip_var.get().strip()]
        equipment_id = self.equipment_label_to_id[self.equipment_item_var.get().strip()]
        quantity = int(self.quantity_allocated_var.get().strip())
        checkout_date = self.checkout_date_var.get().strip()
        return_date = self.return_date_var.get().strip()

        if return_date == "":
            return_date = None

        query = """
            INSERT INTO public.trip_equipment
                (quantityallocated, checkout_date, return_date, trip_id, equipmentid)
            VALUES
                (%s, %s, %s, %s, %s);
        """

        success, message = execute_query(
            query,
            (quantity, checkout_date, return_date, trip_id, equipment_id)
        )

        if success:
            messagebox.showinfo("הצלחה", "הציוד נוסף לטיול בהצלחה")
            self.clear_equipment_form()
            self.load_equipment_table()
        else:
            messagebox.showerror("שגיאה", message)

    def update_trip_equipment(self):
        if not self.validate_equipment_form(require_details=True):
            return

        old_trip_id = self.selected_equipment_old_trip_id
        old_equipment_id = self.selected_equipment_old_equipment_id

        if old_trip_id is None or old_equipment_id is None:
            old_trip_id = self.trip_label_to_id[self.equipment_trip_var.get().strip()]
            old_equipment_id = self.equipment_label_to_id[self.equipment_item_var.get().strip()]

        new_trip_id = self.trip_label_to_id[self.equipment_trip_var.get().strip()]
        new_equipment_id = self.equipment_label_to_id[self.equipment_item_var.get().strip()]
        quantity = int(self.quantity_allocated_var.get().strip())
        checkout_date = self.checkout_date_var.get().strip()
        return_date = self.return_date_var.get().strip()

        if return_date == "":
            return_date = None

        query = """
            UPDATE public.trip_equipment
            SET
                quantityallocated = %s,
                checkout_date = %s,
                return_date = %s,
                trip_id = %s,
                equipmentid = %s
            WHERE trip_id = %s
              AND equipmentid = %s;
        """

        success, message = execute_query(
            query,
            (
                quantity,
                checkout_date,
                return_date,
                new_trip_id,
                new_equipment_id,
                old_trip_id,
                old_equipment_id
            )
        )

        if success:
            messagebox.showinfo("הצלחה", "הציוד לטיול עודכן בהצלחה")
            self.clear_equipment_form()
            self.load_equipment_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_trip_equipment(self):
        if not self.validate_equipment_form(require_details=False):
            return

        confirm = messagebox.askyesno("אישור מחיקה", "האם למחוק את הציוד מהטיול?")

        if not confirm:
            return

        trip_id = self.trip_label_to_id[self.equipment_trip_var.get().strip()]
        equipment_id = self.equipment_label_to_id[self.equipment_item_var.get().strip()]

        query = """
            DELETE FROM public.trip_equipment
            WHERE trip_id = %s
              AND equipmentid = %s;
        """

        success, message = execute_query(query, (trip_id, equipment_id))

        if success:
            messagebox.showinfo("הצלחה", "הציוד נמחק מהטיול בהצלחה")
            self.clear_equipment_form()
            self.load_equipment_table()
        else:
            messagebox.showerror("שגיאה", message)

    # ---------------------------------------------------
    # trip_transportation tab
    # ---------------------------------------------------
    def create_transport_tab(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="פרטי תחבורה לטיול",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            fg="#1f2937",
            padx=12,
            pady=12
        )
        form_frame.pack(fill="x", padx=10, pady=8)

        fields = [
            ("Trip *", self.transport_trip_var, "combo", list(self.trip_label_to_id.keys())),
            ("Transportation *", self.transport_item_var, "combo", list(self.transport_label_to_id.keys())),
            ("Departure YYYY-MM-DD HH:MM:SS *", self.departure_date_time_var, "entry", None),
            ("Arrival YYYY-MM-DD HH:MM:SS *", self.arrival_date_time_var, "entry", None),
        ]

        for index, (label_text, var, widget_type, options) in enumerate(fields):
            label = tk.Label(form_frame, text=label_text, font=("Arial", 10), bg=BG_COLOR)
            label.grid(row=index // 2, column=(index % 2) * 2, padx=8, pady=8, sticky="w")

            if widget_type == "combo":
                widget = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=options,
                    state="readonly",
                    width=42,
                    font=("Arial", 10)
                )

                if label_text.startswith("Trip"):
                    self.transport_trip_combo = widget
                else:
                    self.transport_transport_combo = widget
            else:
                widget = tk.Entry(
                    form_frame,
                    textvariable=var,
                    width=30,
                    font=("Arial", 10)
                )

            widget.grid(row=index // 2, column=(index % 2) * 2 + 1, padx=8, pady=8)

        actions_frame = tk.Frame(parent, bg=BG_COLOR)
        actions_frame.pack(fill="x", padx=10, pady=5)

        buttons = [
            ("שליפה לפי Trip + Transportation", self.load_transport_by_key, BLUE, 30),
            ("הוספה", self.add_trip_transport, GREEN, 12),
            ("עדכון", self.update_trip_transport, ORANGE, 12),
            ("מחיקה", self.delete_trip_transport, RED, 12),
            ("ניקוי שדות", self.clear_transport_form, GRAY, 14),
        ]

        for text, command, color, width in buttons:
            btn = create_button(actions_frame, text, command, color=color, width=width)
            btn.pack(side="left", padx=5)

        table_frame = tk.Frame(parent, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = [
            "trip_name",
            "transport_type",
            "capacity",
            "supplier_name",
            "departure_date_time",
            "arrival_date_time"
        ]

        headings = {
            "trip_name": "Trip",
            "transport_type": "Transport Type",
            "capacity": "Capacity",
            "supplier_name": "Supplier",
            "departure_date_time": "Departure",
            "arrival_date_time": "Arrival"
        }

        self.transport_tree = create_table(table_frame, columns, headings)
        self.transport_tree.bind("<<TreeviewSelect>>", self.on_transport_select)

    def load_transport_table(self):
        if self.transport_tree is None:
            return

        for item in self.transport_tree.get_children():
            self.transport_tree.delete(item)

        rows = fetch_all("""
            SELECT
                tt.trip_id,
                tt.transportid,
                tt.departure_date_time,
                tt.arrival_date_time,
                t.trip_name,
                tr.capacity,
                s.company_name AS supplier_name,
                typ.transport_type_name
            FROM public.trip_transportation tt
            JOIN public.trips t
                ON tt.trip_id = t.trip_id
            JOIN public.transportation tr
                ON tt.transportid = tr.transportid
            JOIN public.supplier s
                ON tr.supplierid = s.supplierid
            JOIN public.transport_types typ
                ON tr.transport_type_id = typ.transport_type_id
            ORDER BY tt.trip_id, tt.departure_date_time;
        """)

        for row in rows:
            item_id = f"transport|{row['trip_id']}|{row['transportid']}|{row['departure_date_time']}"

            self.transport_tree.insert(
                "",
                "end",
                iid=item_id,
                values=[
                    row["trip_name"],
                    row["transport_type_name"],
                    row["capacity"],
                    row["supplier_name"],
                    row["departure_date_time"],
                    row["arrival_date_time"]
                ]
            )

    def clear_transport_form(self):
        self.transport_trip_var.set("")
        self.transport_item_var.set("")
        self.departure_date_time_var.set("")
        self.arrival_date_time_var.set("")

        self.selected_transport_old_trip_id = None
        self.selected_transport_old_transport_id = None
        self.selected_transport_old_departure = None

    def validate_transport_form(self, require_dates=True):
        if not self.transport_trip_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Trip")
            return False

        if self.transport_trip_var.get().strip() not in self.trip_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Trip מתוך הרשימה")
            return False

        if not self.transport_item_var.get().strip():
            messagebox.showwarning("שגיאה", "יש לבחור Transportation")
            return False

        if self.transport_item_var.get().strip() not in self.transport_label_to_id:
            messagebox.showwarning("שגיאה", "יש לבחור Transportation מתוך הרשימה")
            return False

        if require_dates:
            if not self.departure_date_time_var.get().strip():
                messagebox.showwarning("שגיאה", "יש להזין Departure Date Time")
                return False

            if not self.arrival_date_time_var.get().strip():
                messagebox.showwarning("שגיאה", "יש להזין Arrival Date Time")
                return False

        return True

    def on_transport_select(self, event):
        selected = self.transport_tree.selection()

        if not selected:
            return

        item_id = selected[0]

        try:
            _, trip_id_text, transport_id_text, departure_text = item_id.split("|", 3)
            trip_id = int(trip_id_text)
            transport_id = int(transport_id_text)
        except ValueError:
            messagebox.showerror("שגיאה", "לא ניתן לקרוא את התחבורה שנבחרה")
            return

        row = fetch_one("""
            SELECT
                trip_id,
                transportid,
                departure_date_time,
                arrival_date_time
            FROM public.trip_transportation
            WHERE trip_id = %s
              AND transportid = %s
              AND departure_date_time = %s;
        """, (trip_id, transport_id, departure_text))

        if row is None:
            return

        self.selected_transport_old_trip_id = row["trip_id"]
        self.selected_transport_old_transport_id = row["transportid"]
        self.selected_transport_old_departure = row["departure_date_time"]

        self.transport_trip_var.set(self.trip_id_to_label.get(row["trip_id"], ""))
        self.transport_item_var.set(self.transport_id_to_label.get(row["transportid"], ""))
        self.departure_date_time_var.set(row["departure_date_time"])
        self.arrival_date_time_var.set(row["arrival_date_time"])

    def load_transport_by_key(self):
        if not self.validate_transport_form(require_dates=False):
            return

        trip_id = self.trip_label_to_id[self.transport_trip_var.get().strip()]
        transport_id = self.transport_label_to_id[self.transport_item_var.get().strip()]

        row = fetch_one("""
            SELECT
                trip_id,
                transportid,
                departure_date_time,
                arrival_date_time
            FROM public.trip_transportation
            WHERE trip_id = %s
              AND transportid = %s
            ORDER BY departure_date_time
            LIMIT 1;
        """, (trip_id, transport_id))

        if row is None:
            messagebox.showinfo("לא נמצא", "לא נמצאה תחבורה לטיול לפי המפתח שהוזן")
            return

        self.selected_transport_old_trip_id = row["trip_id"]
        self.selected_transport_old_transport_id = row["transportid"]
        self.selected_transport_old_departure = row["departure_date_time"]

        self.departure_date_time_var.set(row["departure_date_time"])
        self.arrival_date_time_var.set(row["arrival_date_time"])

    def add_trip_transport(self):
        if not self.validate_transport_form(require_dates=True):
            return

        trip_id = self.trip_label_to_id[self.transport_trip_var.get().strip()]
        transport_id = self.transport_label_to_id[self.transport_item_var.get().strip()]
        departure = self.departure_date_time_var.get().strip()
        arrival = self.arrival_date_time_var.get().strip()

        query = """
            INSERT INTO public.trip_transportation
                (departure_date_time, arrival_date_time, transportid, trip_id)
            VALUES
                (%s, %s, %s, %s);
        """

        success, message = execute_query(query, (departure, arrival, transport_id, trip_id))

        if success:
            messagebox.showinfo("הצלחה", "התחבורה נוספה לטיול בהצלחה")
            self.clear_transport_form()
            self.load_transport_table()
        else:
            messagebox.showerror("שגיאה", message)

    def update_trip_transport(self):
        if not self.validate_transport_form(require_dates=True):
            return

        old_trip_id = self.selected_transport_old_trip_id
        old_transport_id = self.selected_transport_old_transport_id
        old_departure = self.selected_transport_old_departure

        if old_trip_id is None or old_transport_id is None or old_departure is None:
            messagebox.showwarning(
                "שגיאה",
                "לעדכון צריך קודם לבחור שורה מהטבלה או לבצע שליפה לפי Trip + Transportation."
            )
            return

        new_trip_id = self.trip_label_to_id[self.transport_trip_var.get().strip()]
        new_transport_id = self.transport_label_to_id[self.transport_item_var.get().strip()]
        new_departure = self.departure_date_time_var.get().strip()
        new_arrival = self.arrival_date_time_var.get().strip()

        query = """
            UPDATE public.trip_transportation
            SET
                departure_date_time = %s,
                arrival_date_time = %s,
                transportid = %s,
                trip_id = %s
            WHERE trip_id = %s
              AND transportid = %s
              AND departure_date_time = %s;
        """

        success, message = execute_query(
            query,
            (
                new_departure,
                new_arrival,
                new_transport_id,
                new_trip_id,
                old_trip_id,
                old_transport_id,
                old_departure
            )
        )

        if success:
            messagebox.showinfo("הצלחה", "התחבורה לטיול עודכנה בהצלחה")
            self.clear_transport_form()
            self.load_transport_table()
        else:
            messagebox.showerror("שגיאה", message)

    def delete_trip_transport(self):
        if self.selected_transport_old_trip_id is None:
            if not self.validate_transport_form(require_dates=False):
                return

            self.load_transport_by_key()

            if self.selected_transport_old_trip_id is None:
                return

        confirm = messagebox.askyesno("אישור מחיקה", "האם למחוק את התחבורה מהטיול?")

        if not confirm:
            return

        query = """
            DELETE FROM public.trip_transportation
            WHERE trip_id = %s
              AND transportid = %s
              AND departure_date_time = %s;
        """

        success, message = execute_query(
            query,
            (
                self.selected_transport_old_trip_id,
                self.selected_transport_old_transport_id,
                self.selected_transport_old_departure
            )
        )

        if success:
            messagebox.showinfo("הצלחה", "התחבורה נמחקה מהטיול בהצלחה")
            self.clear_transport_form()
            self.load_transport_table()
        else:
            messagebox.showerror("שגיאה", message)