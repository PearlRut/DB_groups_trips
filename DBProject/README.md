# Group Trips Database System

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