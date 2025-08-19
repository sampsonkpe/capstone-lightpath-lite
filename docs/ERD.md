# Entity Relationship Diagram (ERD) – LightPath Lite

This document represents the database schema for the LightPath Lite backend:
Covering users, passengers, conductors, buses, routes, trips, bookings, and weather integration.

erDiagram
    USER {
        int user_id PK
        string email
        string password
	string role
        datetime created_at
    }

    PASSENGER {
        int passenger_id PK
        int user_id FK
        string name
	string contact_number
        string username
        string email
    }

    CONDUCTOR {
        int conductor_id PK
	int user_id FK
        string name
        string phone_number
        int bus_id FK
        int route_id FK
    }

    BUS {
        int bus_id PK
        int conductor_id FK
        string registration_number
        int capacity
    }

    ROUTE {
        int route_id PK
        int bus_id FK
        string start_location
        string end_location
        decimal distance
        text stop_list
    }

    TRIP {
        int trip_id PK
        datetime date_time
        int bus_id FK
        int route_id FK
        int conductor_id FK
        int total_passengers
        int weather_id FK
    }

    BOOKING {
        int booking_id PK
        int passenger_id FK
        int trip_id FK
        string seat_number
        datetime booking_time
    }

    WEATHER {
        int weather_id PK
        datetime timestamp
        string location
        string condition
        decimal temperature
    }

    %% Relationships
    USER ||--o{ PASSENGER : "can be"
    USER ||--o{ CONDUCTOR : "can be"
    CONDUCTOR ||--o{ BUS : "manages"
    BUS ||--o{ ROUTE : "assigned to"
    ROUTE ||--o{ TRIP : "contains"
    PASSENGER ||--o{ BOOKING : "makes"
    TRIP ||--o{ BOOKING : "has"
    TRIP ||--o{ TICKET : "generates"
    BOOKING ||--o{ PAYMENT : "initiates"
