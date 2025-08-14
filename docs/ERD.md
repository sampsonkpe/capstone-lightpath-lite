# Entity Relationship Diagram (ERD) – LightPath Lite

This diagram represents the database schema for the LightPath Lite backend, covering users, passengers, conductors, buses, routes, trips, bookings, and weather integration.

erDiagram
    USER {
        int id PK
        string username
        string email
        string password
        datetime date_joined
    }

    PASSENGER {
        int passenger_id PK
        string name
        string contact_number
        string username
        string email
    }

    CONDUCTOR {
        int conductor_id PK
        string name
        string phone_number
        int bus_id FK
        int route_id FK
    }

    BUS {
        int bus_id PK
        string registration_number
        int capacity
    }

    ROUTE {
        int route_id PK
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
    PASSENGER ||--o{ BOOKING : "makes"
    BOOKING }o--|| TRIP : "for"
    CONDUCTOR ||--o{ TRIP : "assigned to"
    BUS ||--o{ TRIP : "used for"
    ROUTE ||--o{ TRIP : "taken on"
    TRIP ||--o{ WEATHER : "has"
    CONDUCTOR }o--|| BUS : "operates"
    CONDUCTOR }o--|| ROUTE : "manages"
