# ui_helpers.py

import tkinter as tk
from tkinter import ttk
import platform

IS_MAC = platform.system() == "Darwin"

if IS_MAC:
    try:
        from tkmacosx import Button as MacButton
    except ImportError:
        MacButton = tk.Button
else:
    MacButton = tk.Button


BG_COLOR = "#f4f6f8"
TITLE_COLOR = "#1f2937"
TEXT_COLOR = "#4b5563"

BLUE = "#2563eb"
GREEN = "#059669"
ORANGE = "#d97706"
RED = "#dc2626"
GRAY = "#6b7280"


def create_title(root, text):
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
    if IS_MAC:
        # tkmacosx Button uses pixel sizing instead of character sizing
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
            cursor="hand2"
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
    tree = ttk.Treeview(parent, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=headings.get(col, col))
        tree.column(col, width=145, anchor="center")

    scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)

    tree.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)

    return tree