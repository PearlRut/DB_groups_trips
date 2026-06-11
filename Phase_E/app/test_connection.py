# test_connection.py

from db import test_connection, fetch_all


success, result = test_connection()

if success:
    print("Connection succeeded!")
    print("Database:", result[0])
    print("User:", result[1])

    print("\nChecking trips table...")

    rows = fetch_all("SELECT trip_id, trip_name FROM public.trips LIMIT 5;")

    if rows:
        print("Trips found:")
        for row in rows:
            print(row["trip_id"], "-", row["trip_name"])
    else:
        print("Connected, but no trips were found or table name is different.")

else:
    print("Connection failed!")
    print(result)