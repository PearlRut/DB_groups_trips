import random
from datetime import date, timedelta
import psycopg2

# =====================================================================
# CONFIGURATION - Change these quantities to adjust how much data to add
# =====================================================================
NUM_ROUTES = 10             # How many new routes to add
NUM_TRANSPORTS = 5          # How many new transport types to add
NUM_PARTICIPANTS = 50       # How many new participants to add
NUM_GUIDES = 5              # How many of the new participants to make guides (must be <= NUM_PARTICIPANTS)
NUM_TRIPS = 5               # How many new trips to add
NUM_EVENTS_PER_TRIP = 5     # How many schedules/events/actions to add per trip (change this between 5 and 10)
# =====================================================================

# Connection details for the running PostgreSQL database container on localhost
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="group_trips_db",
        user="postgres",
        password="1234"
    )
    cur = conn.cursor()
    print("Successfully connected to the database.")
except Exception as e:
    print(f"Error connecting to database: {e}")
    exit(1)

# Helper functions for generating random data
def random_date(start_year=2025, end_year=2027):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def random_time_pair():
    start_hour = random.randint(6, 18)
    start_min = random.choice([0, 15, 30, 45])
    duration = random.randint(1, 3)
    end_hour = min(start_hour + duration, 23)
    return f"{start_hour:02d}:{start_min:02d}:00", f"{end_hour:02d}:{start_min:02d}:00"

try:
    # ----------------------------------------------------
    # 1. Add New Routes (routes)
    # ----------------------------------------------------
    print(f"Appending {NUM_ROUTES} new routes...")
    regions = ["North", "South", "Center", "Jerusalem", "Coastal"]
    difficulty_levels = ["Easy", "Medium", "Hard"]
    
    for i in range(1, NUM_ROUTES + 1):
        cur.execute(
            """
            INSERT INTO routes (route_name, region, distance_km, duration_hours, difficulty_level)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (
                f"NewRoute_{random.randint(1000, 9999)}",
                random.choice(regions),
                round(random.uniform(5, 45), 2),
                round(random.uniform(2, 8), 2),
                random.choice(difficulty_levels)
            )
        )
    print("Routes appended successfully.")

    # ----------------------------------------------------
    # 2. Add New Transport Types (transport_types)
    # ----------------------------------------------------
    print(f"Appending {NUM_TRANSPORTS} new transport types...")
    for i in range(1, NUM_TRANSPORTS + 1):
        try:
            cur.execute(
                """
                INSERT INTO transport_types (transport_type_name)
                VALUES (%s);
                """,
                (f"NewTransport_{random.randint(1000, 9999)}",)
            )
        except psycopg2.errors.UniqueViolation:
            conn.rollback() # If unique name collision, skip
            continue
    print("Transport types appended successfully.")

    # ----------------------------------------------------
    # 3. Add New Participants (participants)
    # ----------------------------------------------------
    print(f"Appending {NUM_PARTICIPANTS} new participants...")
    first_names = ["Ruth", "Noa", "Dana", "Yael", "Tamar", "Amit", "Lior", "Shira", "Maya", "Neta"]
    last_names = ["Cohen", "Levi", "Mizrahi", "Peretz", "Avraham", "Biton", "Gold", "David", "Bar", "Sharabi"]
    
    new_participant_ids = []
    for i in range(1, NUM_PARTICIPANTS + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        phone = f"05{random.randint(0,9)}{random.randint(1000000,9999999)}"
        email = f"append_user_{random.randint(10000, 99999)}@example.com"
        birth_date = random_date(1975, 2005).isoformat()
        
        cur.execute(
            """
            INSERT INTO participants (first_name, last_name, phone, email, birth_date)
            VALUES (%s, %s, %s, %s, %s) RETURNING participant_id;
            """,
            (first_name, last_name, phone, email, birth_date)
        )
        new_participant_ids.append(cur.fetchone()[0])
    print("Participants appended successfully.")

    # ----------------------------------------------------
    # 4. Add New Guides (guides) - IS-A Participant
    # ----------------------------------------------------
    print(f"Appending {NUM_GUIDES} new guides...")
    # Select from the newly created participants
    sampled_guide_ids = random.sample(new_participant_ids, min(NUM_GUIDES, len(new_participant_ids)))
    for idx, part_id in enumerate(sampled_guide_ids, start=1):
        cur.execute(
            """
            INSERT INTO guides (participant_id, license_number, experience_years)
            VALUES (%s, %s, %s);
            """,
            (part_id, f"NEW_LIC_{random.randint(10000, 99999)}", random.randint(1, 15))
        )
    print("Guides appended successfully.")

    # ----------------------------------------------------
    # 5. Add New Trips (trips)
    # ----------------------------------------------------
    print(f"Appending {NUM_TRIPS} new trips...")
    # Fetch random existing route_ids and transport_type_ids to link
    cur.execute("SELECT route_id FROM routes ORDER BY random() LIMIT 5;")
    available_route_ids = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT transport_type_id FROM transport_types ORDER BY random() LIMIT 5;")
    available_transport_ids = [row[0] for row in cur.fetchall()]

    trip_statuses = ["Planned", "Open", "Closed", "Active"]
    new_trip_ids = []

    for i in range(NUM_TRIPS):
        start_date = random_date(2026, 2027)
        end_date = start_date + timedelta(days=random.randint(1, 5))
        group_size = random.randint(10, 40)
        route_id = available_route_ids[i % len(available_route_ids)]
        transport_id = available_transport_ids[i % len(available_transport_ids)]
        
        cur.execute(
            """
            INSERT INTO trips (trip_name, start_date, end_date, group_size, status, route_id, transport_type_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING trip_id;
            """,
            (f"AppendTrip_{random.randint(100, 999)}", start_date.isoformat(), end_date.isoformat(), 
             group_size, random.choice(trip_statuses), route_id, transport_id)
        )
        new_trip_ids.append(cur.fetchone()[0])
    print("Trips appended successfully.")

    # ----------------------------------------------------
    # 6. Link participants to trips (trip_participants)
    # ----------------------------------------------------
    print("Linking participants to trips...")
    for trip_id in new_trip_ids:
        # Register random new participants to this trip
        sampled_participants = random.sample(new_participant_ids, random.randint(3, 8))
        for part_id in sampled_participants:
            cur.execute(
                """
                INSERT INTO trip_participants (trip_id, participant_id)
                VALUES (%s, %s) ON CONFLICT DO NOTHING;
                """,
                (trip_id, part_id)
            )
    print("Participants linked successfully.")

    # ----------------------------------------------------
    # 7. Add Schedules, Events, and Actions for the new trips
    # ----------------------------------------------------
    print(f"Adding schedules, events, and actions for the new trips (Quantity: {NUM_EVENTS_PER_TRIP} per trip)...")
    for trip_id in new_trip_ids:
        # Create NUM_EVENTS_PER_TRIP schedule items, events, and actions for this trip
        for order_num in range(1, NUM_EVENTS_PER_TRIP + 1):
            start_time, end_time = random_time_pair()
            sch_date = random_date(2026, 2026).isoformat()
            
            cur.execute(
                """
                INSERT INTO schedules (trip_id, order_num, start_time, end_time, description, sch_date)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (trip_id, order_num, start_time, end_time, f"Schedule {order_num} for appended trip {trip_id}", sch_date)
            )
            
            # Create 1 event linked to this schedule item
            cur.execute(
                """
                INSERT INTO events (event_name, event_date, start_hour, end_hour, cost, status, trip_id, order_num)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING event_id;
                """,
                (
                    f"AppendEvent_{random.randint(100, 999)}",
                    sch_date,
                    start_time,
                    end_time,
                    round(random.uniform(0, 150), 2),
                    "Scheduled",
                    trip_id,
                    order_num
                )
            )
            event_id = cur.fetchone()[0]
            
            # Create 1 action linked to this event
            action_types = ["Info", "Logistics", "Safety", "Briefing", "Check"]
            cur.execute(
                """
                INSERT INTO actions (address, action_type, action_name, event_id)
                VALUES (%s, %s, %s, %s);
                """,
                (
                    f"AppendAddress_{random.randint(100, 999)}",
                    random.choice(action_types),
                    f"AppendAction_{random.randint(100, 999)}",
                    event_id
                )
            )
            
    # Commit transaction
    conn.commit()
    print("New test data appended successfully to all 9 original tables without wiping any existing data!")

except Exception as e:
    conn.rollback()
    print(f"An error occurred: {e}")
    print("Transaction rolled back.")

finally:
    cur.close()
    conn.close()

# how to run : python3 scripts/append_data_direct.py

