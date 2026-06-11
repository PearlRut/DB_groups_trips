# db.py

import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG


def get_connection():
    """
    Creates a connection to the PostgreSQL database.
    """
    return psycopg2.connect(**DB_CONFIG)


def test_connection():
    """
    Tests the database connection.
    """
    conn = None

    try:
        conn = get_connection()

        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user;")
            result = cur.fetchone()

        return True, result

    except Exception as e:
        return False, str(e)

    finally:
        if conn:
            conn.close()


def fetch_all(query, params=None):
    """
    Executes SELECT query and returns all rows.
    """
    conn = None

    try:
        conn = get_connection()

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

        return rows

    except Exception as e:
        print("Database fetch error:", e)
        return []

    finally:
        if conn:
            conn.close()


def fetch_one(query, params=None):
    """
    Executes SELECT query and returns one row.
    """
    conn = None

    try:
        conn = get_connection()

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone()

        return row

    except Exception as e:
        print("Database fetch one error:", e)
        return None

    finally:
        if conn:
            conn.close()


def execute_query(query, params=None):
    """
    Executes INSERT / UPDATE / DELETE / CALL queries.
    """
    conn = None

    try:
        conn = get_connection()

        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()

        return True, "הפעולה בוצעה בהצלחה"

    except Exception as e:
        if conn:
            conn.rollback()

        return False, str(e)

    finally:
        if conn:
            conn.close()