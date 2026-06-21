# main.py
# קובץ נקודת הכניסה הראשי של האפליקציה (Entry Point)

import tkinter as tk
from app_controller import AppController


if __name__ == "__main__":
    # יצירת חלון האב של Tkinter (החלון הראשי של המערכת)
    root = tk.Tk()
    
    # אתחול ה-Controller שמנהל את כל המסכים ומעביר ביניהם
    app = AppController(root)
    
    # הפעלת לולאת האירועים המרכזית של Tkinter לשמירת החלון פתוח ומגיב
    root.mainloop()