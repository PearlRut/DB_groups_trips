# db.py
# קובץ התקשרות למסד הנתונים - מכיל פונקציות עזר לביצוע שאילתות מול PostgreSQL

import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG


def get_connection():
    """
    יוצר חיבור פיזי למסד הנתונים של PostgreSQL באמצעות הספרייה psycopg2.
    הפונקציה משתמשת במילון ההגדרות DB_CONFIG (על ידי פריסתו בעזרת **).
    """
    return psycopg2.connect(**DB_CONFIG)


def test_connection():
    """
    בודק את תקינות החבור למסד הנתונים.
    מחזיר Tuple של (האם הצליח, תוצאת בדיקה/הודעת שגיאה).
    """
    conn = None

    try:
        conn = get_connection()

        # שימוש ב-Context Manager (with) של cursor
        # cursor הוא האובייקט שדרכו אנו שולחים פקודות SQL ומקבלים תוצאות
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user;")
            result = cur.fetchone()

        return True, result

    except Exception as e:
        return False, str(e)

    finally:
        # סגירה תמידית של החיבור בבלוק finally כדי למנוע דליפת משאבים וחיבורים פתוחים ב-DB
        if conn:
            conn.close()


def fetch_all(query, params=None):
    """
    מבצע שאילתת SELECT ומחזיר את כל השורות שנמצאו.
    שימוש ב-RealDictCursor מאפשר לקבל כל שורה כמילון פייתון (dict) שבו המפתחות הם שמות העמודות ב-SQL,
    מה שמקל על הצגת הנתונים בטבלאות ב-UI (למשל: row["participant_id"]).
    """
    conn = None

    try:
        conn = get_connection()

        # RealDictCursor הופך את השורות שחוזרות לרשומות במבנה מפתח-ערך במקום Tuple פשוט
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall() # שליפת כל השורות שחזרו מהשאילתה

        return rows

    except Exception as e:
        print("Database fetch error:", e)
        return []

    finally:
        if conn:
            conn.close()


def fetch_one(query, params=None):
    """
    מבצע שאילתת SELECT ומחזיר שורה אחת בלבד (או None אם לא נמצאה רשומה מתאימה).
    מתאים לשליפת רשומה ספציפית לפי מפתח ראשי (ID).
    """
    conn = None

    try:
        conn = get_connection()

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone() # שליפת שורה בודדת בלבד

        return row

    except Exception as e:
        print("Database fetch one error:", e)
        return None

    finally:
        if conn:
            conn.close()


def execute_query(query, params=None):
    """
    מבצע שאילתות לשינוי נתונים: INSERT, UPDATE, DELETE או קריאה לפרוצדורות (CALL).
    במקרה של הצלחה, מבצע commit לשמירת השינויים בבסיס הנתונים.
    במקרה של שגיאה, מבצע rollback לביטול הפעולה והחזרת המצב לקדמותו.
    """
    conn = None

    try:
        conn = get_connection()

        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit() # שמירה פיזית של השינויים (INSERT/UPDATE/DELETE) ב-DB

        return True, "הפעולה בוצעה בהצלחה"

    except Exception as e:
        # במקרה של שגיאה (למשל: הפרת מגבלת מפתח זר או ייחודיות) - נבצע ביטול (rollback)
        if conn:
            conn.rollback()

        return False, str(e)

    finally:
        if conn:
            conn.close()