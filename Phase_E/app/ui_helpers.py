# ui_helpers.py
# קובץ עזרי ממשק משתמש - מכיל פונקציות לעיצוב ויצירת רכיבים גרפיים של Tkinter בצורה אחידה

import tkinter as tk
from tkinter import ttk
import platform

# בדיקה האם האפליקציה רצה על מערכת הפעלה macOS (Darwin)
IS_MAC = platform.system() == "Darwin"

# ב-macOS, רכיב הכפתור הסטנדרטי של Tkinter אינו תומך בשינוי צבע רקע וגבולות בצורה טובה.
# לכן, אנו מנסים לייבא את הספרייה tkmacosx שפותרת בעיה זו. אם היא אינה מותקנת, נחזור לפתרון ברירת המחדל.
if IS_MAC:
    try:
        from tkmacosx import Button as MacButton
    except ImportError:
        MacButton = tk.Button
else:
    MacButton = tk.Button


# הגדרת פאלת הצבעים המודרנית של המערכת (Color Palette)
BG_COLOR = "#f4f6f8"       # צבע רקע בהיר (Light Gray)
TITLE_COLOR = "#1f2937"    # צבע כותרות כהה
TEXT_COLOR = "#4b5563"     # צבע טקסט רגיל

# צבעי מפתח לפעולות השונות
BLUE = "#2563eb"           # פעולות כלליות, ניווט ושליפה (שליפה לפי ID)
GREEN = "#059669"          # הוספה או שמירה (יצירת רשומות חדשות)
ORANGE = "#d97706"         # עדכון רשומה קיימת
RED = "#dc2626"            # מחיקה
GRAY = "#6b7280"           # ביטול, ניקוי שדות, חזרה למסך קודם


def create_title(root, text):
    """
    יוצר ומציג כותרת ראשית מעוצבת במסך.
    """
    title = tk.Label(
        root,
        text=text,
        font=("Arial", 24, "bold"),
        bg=BG_COLOR,
        fg=TITLE_COLOR
    )
    title.pack(pady=20)
    return title


def create_subtitle(root, text):
    """
    יוצר ומציג כותרת משנית מעוצבת במסך.
    """
    subtitle = tk.Label(
        root,
        text=text,
        font=("Arial", 14),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )
    subtitle.pack(pady=5)
    return subtitle


def create_button(parent, text, command, color=BLUE, width=24):
    """
    מייצר כפתור מעוצב התומך הן ב-Windows/Linux והן ב-macOS.
    """
    if IS_MAC:
        # כפתורים של tkmacosx משתמשים בפיקסלים לחישוב רוחב/גובה במקום מספר תווים ב-Tkinter רגיל.
        # לכן, אנו מכפילים את הרוחב כדי לשמור על יחס פרופורציונלי.
        pixel_width = width * 8.5
        pixel_height = 40
        button = MacButton(
            parent,
            text=text,
            command=command,
            width=pixel_width,
            height=pixel_height,
            font=("Arial", 11),
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            cursor="hand2" # משנה את סמן העכבר ליד בלחיצה
        )
    else:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            height=2,
            font=("Arial", 11),
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        )
    return button


def create_table(parent, columns, headings):
    """
    מייצר טבלה (Treeview) מעוצבת עם פסי גלילה אנכיים ואופקיים בתוך Grid.
    """
    # יצירת אובייקט ה-Treeview המציג עמודות וכותרות
    tree = ttk.Treeview(parent, columns=columns, show="headings")

    # מעבר על כל העמודות והגדרת הכותרות והיישור שלהן למרכז
    for col in columns:
        tree.heading(col, text=headings.get(col, col))
        tree.column(col, width=145, anchor="center")

    # יצירת פסי גלילה (Scrollbars)
    scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)

    # קישור פסי הגלילה לטבלה
    tree.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    # מיקום הרכיבים ב-Grid בתוך הפאנל שלהם
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    # הגדרת גדילה אוטומטית (weight) כדי שהטבלה תתפרס על כל השטח הפנוי
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)

    return tree