import random
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="group_trips_db",
    user="postgres",
    password="1234"
)

cur = conn.cursor()

action_types = ["Info", "Logistics", "Safety", "Briefing", "Check"]

rows = []
for event_id in range(1, 501):
    rows.append((
        f"DirectAddress_{event_id}",
        random.choice(action_types),
        f"DirectAction_{event_id}",
        event_id
    ))

cur.executemany(
    """
    INSERT INTO actions (address, action_type, action_name, event_id)
    VALUES (%s, %s, %s, %s)
    """,
    rows
)

conn.commit()
cur.close()
conn.close()

print("Inserted 500 rows into actions directly from Python.")