# API Endpoints – LightPath Lite

This document outlines the core API routes for the **LightPath Lite** backend, grouped by functionality.  
All endpoints follow RESTful conventions and use JSON for request and response bodies unless stated otherwise.

---

## 1. Authentication & Users
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/auth/register/` | POST | Register a new user account | No |
| `/api/auth/login/` | POST | Login and obtain authentication token | No |
| `/api/auth/logout/` | POST | Logout current user (invalidate token) | Yes |
| `/api/auth/profile/` | GET | Retrieve authenticated user profile | Yes |
| `/api/auth/profile/` | PUT | Update authenticated user profile | Yes |
| `/api/auth/change-password/` | POST | Change user password | Yes |

---

## 2. Passengers
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/passengers/` | GET | List all passengers (admin only) | Yes (Admin) |
| `/api/passengers/<id>/` | GET | Retrieve passenger details | Yes |
| `/api/passengers/` | POST | Create new passenger profile | Yes |
| `/api/passengers/<id>/` | PUT | Update passenger profile | Yes |
| `/api/passengers/<id>/` | DELETE | Delete passenger profile | Yes (Admin) |

---

## 3. Conductors
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/conductors/` | GET | List all conductors | Yes |
| `/api/conductors/<id>/` | GET | Retrieve conductor details | Yes |
| `/api/conductors/` | POST | Create new conductor record | Yes (Admin) |
| `/api/conductors/<id>/` | PUT | Update conductor details | Yes |
| `/api/conductors/<id>/` | DELETE | Delete conductor record | Yes (Admin) |

---

## 4. Buses
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/buses/` | GET | List all buses | Yes |
| `/api/buses/<id>/` | GET | Retrieve bus details | Yes |
| `/api/buses/` | POST | Create new bus record | Yes (Admin) |
| `/api/buses/<id>/` | PUT | Update bus details | Yes |
| `/api/buses/<id>/` | DELETE | Delete bus record | Yes (Admin) |

---

## 5. Routes
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/routes/` | GET | List all routes | No |
| `/api/routes/<id>/` | GET | Retrieve route details | No |
| `/api/routes/` | POST | Create new route | Yes (Admin) |
| `/api/routes/<id>/` | PUT | Update route details | Yes (Admin) |
| `/api/routes/<id>/` | DELETE | Delete route | Yes (Admin) |

---

## 6. Trips
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/trips/` | GET | List all trips | No |
| `/api/trips/<id>/` | GET | Retrieve trip details | No |
| `/api/trips/` | POST | Create new trip | Yes (Admin) |
| `/api/trips/<id>/` | PUT | Update trip details | Yes (Admin) |
| `/api/trips/<id>/` | DELETE | Delete trip | Yes (Admin) |

---

## 7. Bookings
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/bookings/` | GET | List all bookings (admin only) | Yes (Admin) |
| `/api/bookings/my/` | GET | List bookings for current user | Yes |
| `/api/bookings/<id>/` | GET | Retrieve booking details | Yes |
| `/api/bookings/` | POST | Create new booking | Yes |
| `/api/bookings/<id>/` | PUT | Update booking details | Yes |
| `/api/bookings/<id>/` | DELETE | Cancel booking | Yes |

---

## 8. Weather (OpenWeather API Integration)
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/weather/current/` | GET | Get current weather for a given location | No |
| `/api/weather/trip/<trip_id>/` | GET | Get weather forecast for a trip's route | No |

---

## Notes
- Auth Required: Indicates whether authentication is needed.  
- `Yes (Admin)` means only admin users can access the endpoint.  
- Authentication uses JWT tokens.  
- All requests and responses use JSON unless otherwise noted.
- `{id}` denotes a resource’s unique identifier.
- `{location}` is a city or region name, e.g., `Accra` or `Dansoman`.
