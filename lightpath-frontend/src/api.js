const BASE_URL = "http://127.0.0.1:8000/api/core";

// Save and retrieve JWT tokens
export const saveToken = (access, refresh) => {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
};

export const getAccessToken = () => localStorage.getItem("access_token");

// Generic GET request with JWT
const get = async (endpoint) => {
  try {
    const res = await fetch(`${BASE_URL}/${endpoint}/`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getAccessToken()}`,
      },
    });
    if (!res.ok) throw new Error(`GET ${endpoint} failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(err);
    return { error: err.message };
  }
};

// Generic POST request with JWT
const post = async (endpoint, data) => {
  try {
    const res = await fetch(`${BASE_URL}/${endpoint}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getAccessToken()}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`POST ${endpoint} failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(err);
    return { error: err.message };
  }
};

// Login function
export const login = async (email, password) => {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/token/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (data.access && data.refresh) {
      saveToken(data.access, data.refresh);
    }
    return data;
  } catch (err) {
    console.error(err);
    return { error: err.message };
  }
};

// Bus-related API calls
export const getBuses = () => get("buses");

// Trip-related API calls
export const getTrips = (busId) => {
  const endpoint = busId ? `trips?bus=${busId}` : "trips";
  return get(endpoint);
};

export const getTripdetails = (tripId) => get(`trips/${tripId}`);

// Fetch all bookings (admin)
export const getBookings = () => get("bookings/my");

export const bookSeat = (tripId, seatNumber, passengerId) =>
  post("bookings/", { trip_id: tripId, seat_number: seatNumber, passenger_id: passengerId });

// --- Payment APIs ---
export const makePayment = (bookingId, amount, method) =>
  post("payments/", { booking_id: bookingId, amount, method });

// --- Profile APIs ---
export const getProfile = (userId) => get(`users/${userId}`);
export const updateProfile = (userId, data) => post(`users/${userId}`, data);

// --- Weather API ---
export const getWeather = () => get("weather/current");