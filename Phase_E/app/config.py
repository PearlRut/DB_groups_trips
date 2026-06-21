# config.py
# קובץ הגדרות ותצורת המערכת - טוען משתני סביבה ומגדיר את פרטי ההתחברות למסד הנתונים

import os
from dotenv import load_dotenv, find_dotenv

# טעינת קובץ ה-.env מתיקיית הפרויקט הנוכחית (usecwd=True)
# הקובץ מכיל את פרטי הגישה השמורים ל-Database (host, port, user, password, database)
load_dotenv(find_dotenv(usecwd=True))

# מילון המכיל את הגדרות ההתחברות לפרוטוקול PostgreSQL
# משתמש ב-os.getenv כדי למשוך את הערכים מקובץ ה-.env, עם ערכי ברירת מחדל במידה ולא נמצאו
DB_CONFIG = {
    "host": os.getenv("PHASE_E_DB_HOST", "localhost"),
    "database": os.getenv("PHASE_E_DB_NAME", "unified_db"),
    "user": os.getenv("PHASE_E_DB_USER", "postgres"),
    "password": os.getenv("PHASE_E_DB_PASSWORD"),
    "port": int(os.getenv("PHASE_E_DB_PORT", "5432"))
}