# Entity Relationship Diagram (ERD) – LightPath Lite

This ERD models the backend schema for **LightPath Lite**, a REST API for managing and tracking public transport routes in Accra.
It covers users, passengers, conductors, buses, routes, trips, bookings, payments, and tickets.

---

## Schema Overview
- **USER**: Stores authentication details (email, password, role).
- **PASSENGER**: Profile for commuters, linked to a user.
- **CONDUCTOR**: Profile for conductors, linked to a user.
- **BUS**: Contains bus details, each linked to a conductor.
- **ROUTE**: Defines start/end locations and stop lists.
- **WEATHER**: Stores weather data affecting trips.
- **TRIP**: Connects a bus, route, conductor, and weather at a scheduled date/time.
- **BOOKING**: Reservation by a passenger for a trip.
- **PAYMENT**: Linked to a booking, tracks transaction status.
- **TICKET**: Generated for a booking, contains a QR code.

---

## ER Diagram

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
        string full_name
        string contact_number
        string username
    }

    CONDUCTOR {
        int conductor_id PK
        int user_id FK
        string full_name
        string phone_number
    }

    BUS {
        int bus_id PK
        string registration_number
        int capacity
        int conductor_id FK
    }

    ROUTE {
        int route_id PK
        string start_location
        string end_location
        decimal distance
        text stop_list
    }

    WEATHER {
        int weather_id PK
        datetime timestamp
        string location
        string condition
        decimal temperature
    }

    TRIP {
        int trip_id PK
        datetime date_time
        int bus_id FK
        int route_id FK
        int conductor_id FK
        int weather_id FK
        int total_passengers
    }

    BOOKING {
        int booking_id PK
        int passenger_id FK
        int trip_id FK
        string seat_number
        datetime booking_time
    }

    PAYMENT {
        int payment_id PK
        int booking_id FK
        decimal amount
        string status
        datetime payment_time
    }

    TICKET {
        int ticket_id PK
        int booking_id FK
        int trip_id FK
        string seat_number
        datetime issued_at
    }

    %% Relationships
    USER ||--o{ PASSENGER : "can be"
    USER ||--o{ CONDUCTOR : "can be"
    CONDUCTOR ||--o{ BUS : "manages"
    BUS ||--o{ TRIP : "assigned to"
    ROUTE ||--o{ TRIP : "defines"
    WEATHER ||--o{ TRIP : "affects"
    PASSENGER ||--o{ BOOKING : "makes"
    TRIP ||--o{ BOOKING : "allows"
    BOOKING ||--|| TICKET : "generates"
    BOOKING ||--o{ PAYMENT : "initiates"