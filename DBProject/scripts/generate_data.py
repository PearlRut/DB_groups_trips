import csv
import random
from datetime import date, timedelta

random.seed(42)

DATA_DIR = "data"

def random_date(start_year=2024, end_year=2027):
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

def write_csv(filename, header, rows):
    with open(f"{DATA_DIR}/{filename}", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

# 1) routes - 500
routes = []
difficulty_levels = ["Easy", "Medium", "Hard"]
regions = ["North", "South", "Center", "Jerusalem", "Coastal"]
for i in range(1, 501):
    routes.append([
        f"Route_{i}",
        random.choice(regions),
        round(random.uniform(1, 50), 2),
        round(random.uniform(1, 12), 2),
        random.choice(difficulty_levels)
    ])
write_csv(
    "routes.csv",
    ["route_name", "region", "distance_km", "duration_hours", "difficulty_level"],
    routes
)

# 2) transport_types - 500
transport_types = [[f"Transport_{i}"] for i in range(1, 501)]
write_csv(
    "transport_types.csv",
    ["transport_type_name"],
    transport_types
)

# 3) participants - 20000
first_names = ["Ruth", "Noa", "Dana", "Yael", "Tamar", "Amit", "Lior", "Shira", "Maya", "Neta"]
last_names = ["Cohen", "Levi", "Mizrahi", "Peretz", "Avraham", "Biton", "Gold", "David", "Bar", "Sharabi"]

participants = []
for i in range(1, 20001):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    phone = f"05{random.randint(0,9)}{random.randint(1000000,9999999)}"
    email = f"user{i}@example.com"
    birth_date = random_date(1970, 2007).isoformat()
    participants.append([first_name, last_name, phone, email, birth_date])

write_csv(
    "participants.csv",
    ["first_name", "last_name", "phone", "email", "birth_date"],
    participants
)

# 4) trips - 500
trip_statuses = ["Planned", "Open", "Closed", "Active"]
trips = []
for i in range(1, 501):
    start_date = random_date(2025, 2027)
    end_date = start_date + timedelta(days=random.randint(1, 7))
    group_size = random.randint(5, 50)
    trips.append([
        f"Trip_{i}",
        start_date.isoformat(),
        end_date.isoformat(),
        group_size,
        random.choice(trip_statuses),
        random.randint(1, 500),   # route_id
        random.randint(1, 500)    # transport_type_id
    ])

write_csv(
    "trips.csv",
    ["trip_name", "start_date", "end_date", "group_size", "status", "route_id", "transport_type_id"],
    trips
)

# 5) guides - 500
guide_ids = random.sample(range(1, 20001), 500)
guides = []
for idx, participant_id in enumerate(guide_ids, start=1):
    guides.append([
        participant_id,
        f"LIC_{idx}",
        random.randint(0, 30)
    ])

write_csv(
    "guides.csv",
    ["participant_id", "license_number", "experience_years"],
    guides
)

# 6) schedules - 500, unique (trip_id, order_num)
schedules = []
used_schedule_keys = set()

while len(schedules) < 500:
    trip_id = random.randint(1, 500)
    order_num = random.randint(1, 20)
    key = (trip_id, order_num)
    if key in used_schedule_keys:
        continue
    used_schedule_keys.add(key)

    start_time, end_time = random_time_pair()
    sch_date = random_date(2025, 2027).isoformat()
    description = f"Schedule item {len(schedules) + 1}"

    schedules.append([
        trip_id,
        order_num,
        start_time,
        end_time,
        description,
        sch_date
    ])

write_csv(
    "schedules.csv",
    ["trip_id", "order_num", "start_time", "end_time", "description", "sch_date"],
    schedules
)

# 7) events - 500, linked to schedules
event_statuses = ["Scheduled", "Open", "Closed", "Active"]
events = []
for i, row in enumerate(schedules, start=1):
    trip_id, order_num, _, _, _, sch_date = row
    start_hour, end_hour = random_time_pair()
    events.append([
        f"Event_{i}",
        sch_date,
        start_hour,
        end_hour,
        round(random.uniform(0, 500), 2),
        random.choice(event_statuses),
        trip_id,
        order_num
    ])

write_csv(
    "events.csv",
    ["event_name", "event_date", "start_hour", "end_hour", "cost", "status", "trip_id", "order_num"],
    events
)

# 8) actions - 500, linked to events
action_types = ["Info", "Logistics", "Safety", "Briefing", "Check"]
actions = []
for event_id in range(1, 501):
    actions.append([
        f"Address_{event_id}",
        random.choice(action_types),
        f"Action_{event_id}",
        event_id
    ])

write_csv(
    "actions.csv",
    ["address", "action_type", "action_name", "event_id"],
    actions
)

# 9) trip_participants - 20000 unique pairs
trip_participants = []
used_tp = set()

while len(trip_participants) < 20000:
    trip_id = random.randint(1, 500)
    participant_id = random.randint(1, 20000)
    key = (trip_id, participant_id)
    if key in used_tp:
        continue
    used_tp.add(key)
    trip_participants.append([trip_id, participant_id])

write_csv(
    "trip_participants.csv",
    ["trip_id", "participant_id"],
    trip_participants
)

print("All CSV files generated successfully.")