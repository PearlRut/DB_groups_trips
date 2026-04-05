# Group Trips Database System

# Ruth Ulman 325442259
# Michal Swissa 326002813

## Introduction

This project presents the design and implementation of a relational database system for managing organized group trips.

The system manages key entities such as participants, trips, guides, routes, schedules, events, and actions. It allows tracking trip activities, organizing participants into trips, and maintaining structured and consistent data.

The system was designed using a top-down approach. First, system screens were defined using AI tools, and based on them, a relational database schema was created using ERDPlus. The database was normalized to Third Normal Form (3NF) to ensure data consistency and eliminate redundancy.

The project also demonstrates multiple methods of data insertion, including SQL INSERT statements, CSV file import using PostgreSQL COPY, direct insertion using Python, and external data generation using Mockaroo.

Finally, the database was backed up and restored to verify data integrity and system reliability.

## System Screens (Google AI Studio)

The system interface was designed using Google AI Studio as part of the top-down design approach. These screens define the main functionality of the system and guided the database design.

### Trips Management Screen
This screen presents all available trips, including key details such as destination, duration, distance, and assigned transport type.
![Trips](images/IMG_4488.JPG)

### Transport Types Screen
Displays the available transportation options used in the system, such as buses, private vehicles, and off-road vehicles.
![Transport](images/IMG_4489.JPG)

### Participants Management Screen
Shows all participants registered in the system, including personal details such as name, phone number, and email.
![Participants](images/IMG_4490.JPG)

### Guides Management Screen
Displays all guides in the system, including their experience, license information, and contact details.
![Guides](images/IMG_4491.JPG)

### Trips Detailed View
Provides detailed information about each trip, including assigned route, guide, and number of participants.
![Trips Details](images/IMG_4492.JPG)

### Events Screen
Displays events related to trips, including date, time, and pricing details.
![Events](images/IMG_4493.JPG)

### Schedule Screen
Shows the timeline of activities within a trip, allowing structured planning of events and actions.
![Schedule](images/IMG_4494.JPG)

### Activities Screen
Displays all activities available in the system, such as games or food-related events.
![Activities](images/IMG_4495.JPG)



## Database Design

The database schema was designed using ERDPlus and includes the main entities required for the system, their attributes, and the relationships between them.

### ERD Diagram
The Entity Relationship Diagram presents the logical design of the system, including the main entities and their relationships.
![ERD](images/erd.png)

### DSD Diagram
The Database Schema Diagram presents the relational schema after conversion from the ERD model into database tables.
![DSD](images/dsd.png)

### Design Decisions
The database was designed to ensure:
- clear entity separation
- proper use of primary and foreign keys
- support for many-to-many relationships through linking tables
- reduction of redundancy
- normalization up to Third Normal Form (3NF)




## SQL Scripts

The following SQL scripts were created and used in the project:

- [Create Tables](init-db/01-create-tables.sql)
- [Drop Tables](init-db/dropTables.sql)
- [Insert Data](init-db/insertTables.sql)
- [Select Queries](init-db/selectAll.sql)
- [Load Data from CSV](init-db/loadFromCsv.sql)

### Additional Scripts
- [Count Rows](init-db/countRows.sql)

### Python Scripts
- [Generate Data](scripts/generate_data.py)
- [Insert Data Directly (Python)](scripts/insert_actions_direct.py)





### Data Insertion Methods

In this section, we document all three required data insertion methods, including screenshots before and after each process.

---
### Data Insertion Methods

In this section, we document all required data insertion methods, including screenshots before and after each process.

---

#### 1. Manual SQL INSERT (Table: actions)

We inserted a new record manually into the `actions` table using an SQL INSERT command.
The inserted record included the following values: address "Tel Aviv", action type "Manual Insert", action name "Test Action Manual", and event ID 1.

After executing the query, we verified the insertion by retrieving the latest records from the table and confirming that the new row was successfully added.

![Manual Insert Result](images/actionsAfter.png)

---

#### 2. Python Direct Insertion (Table: actions)

We used a Python script (`insert_actions_direct.py`) to insert data directly into the database.  
This script programmatically inserted 500 rows into the `actions` table.

After running the script, we verified the insertion by checking the total number of rows in the table and confirming that the count increased accordingly.

![Python Insert](images/method_python.png)

---

#### 3. CSV File Insertion (Table: routes)

We inserted data into the `routes` table using a CSV file and PostgreSQL COPY command.

Before performing the insertion, the table contained only the original dataset:

![Before CSV Insert](images/routesBefor.png)

We then prepared a CSV file containing the new route data:

![CSV File](images/csv.png)

After executing the COPY command, the new data was successfully inserted into the table.

![After CSV Insert](images/routesAfter.png)

---

#### 4. External Data Source – Mockaroo (Table: participants)

We generated a large dataset of participants using the Mockaroo platform and imported it into the database.

This allowed us to efficiently populate the `participants` table with realistic test data.

![Mockaroo Data](images/mockaroo.png)

After the import, we verified that the table contains 20,500 records.

---

### Backup & Restore

#### Backup

We created a full backup of the database using pgAdmin to ensure data safety and recovery capability.

![Backup Step 1](images/backup1.png)
![Backup Step 2](images/backup2.png)

The backup file created:
backup_2026-04-03.backup

---

#### Restore

We restored the database into a separate database named `group_trips_restore` using the backup file.

![Restore Step 1](images/restore1.png)
![Restore Step 2](images/restore2.png)

The restore process completed successfully, and all data was fully recovered and verified.

---

### Summary

All required data insertion methods were successfully implemented and validated:

- Manual SQL insertion into the `actions` table
- Python-based insertion into the `actions` table
- CSV-based insertion into the `routes` table
- External data generation using Mockaroo for the `participants` table
- Full database backup and restore operations

Each step was documented and verified using screenshots.







## Project Structure

- data/ – CSV files used for data insertion
- images/ – screenshots and diagrams
- init-db/ – SQL scripts for database setup
- scripts/ – Python scripts for data generation and insertion
- README.md – project documentation




## How to Run the Project

1. Start the database using Docker:
   docker-compose up -d

2. Create tables:
   run init-db/01-create-tables.sql

3. Insert initial data:
   run init-db/insertTables.sql

4. Load CSV data:
   run init-db/loadFromCsv.sql

5. Run Python script:
   python3 scripts/insert_actions_direct.py




   - Main Project:  
  https://github.com/PearlRut/Group_Trips/tree/main/DBProject


  - Backup File:  
  https://github.com/PearlRut/Group_Trips/tree/main/DBProject/data