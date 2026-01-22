import React, { useState, useEffect } from "react";
import { getBuses, getTrips, getBookings, getWeather } from "../api";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const [buses, setBuses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({ tripsToday: 0, bookings: 0, availableSeats: 0 });
  const [weather, setWeather] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const busData = await getBuses();
        const tripData = await getTrips();
        const bookingData = await getBookings();
        const weatherData = await getWeather();

        if (busData.error) throw new Error(busData.error);

        setBuses(Array.isArray(busData) ? busData : busData.results);
        setStats({
          tripsToday: tripData.length,
          bookings: bookingData.length,
          availableSeats: busData.reduce((acc, bus) => acc + bus.capacity, 0) - bookingData.length
        });
        setWeather(weatherData || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleViewTrips = (busId) => {
    if (!busId) return;
    navigate(`/trips/${busId}`);
  };

  if (loading) return <p className="p-6 text-gray-500">Loading dashboard...</p>;
  if (error) return <p className="p-6 text-red-500">{error}</p>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-blue-700">Dashboard</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-100 p-4 rounded shadow">
          <h2 className="font-semibold">Total Trips Today</h2>
          <p className="text-2xl font-bold">{stats.tripsToday}</p>
        </div>
        <div className="bg-green-100 p-4 rounded shadow">
          <h2 className="font-semibold">Bookings</h2>
          <p className="text-2xl font-bold">{stats.bookings}</p>
        </div>
        <div className="bg-yellow-100 p-4 rounded shadow">
          <h2 className="font-semibold">Available Seats</h2>
          <p className="text-2xl font-bold">{stats.availableSeats}</p>
        </div>
      </div>

      {/* Buses Table */}
      <div className="overflow-x-auto">
        <h2 className="text-xl font-semibold mb-2">Available Buses</h2>
        <table className="min-w-full bg-white border border-gray-200 rounded-lg shadow-sm">
          <thead className="bg-blue-50">
            <tr>
              <th className="text-left p-3 border-b">Registration</th>
              <th className="text-left p-3 border-b">Capacity</th>
              <th className="text-left p-3 border-b">Conductor</th>
              <th className="text-left p-3 border-b">Route</th>
              <th className="text-center p-3 border-b">Actions</th>
            </tr>
          </thead>
          <tbody>
            {buses.map((bus, idx) => (
              <tr key={bus.bus_id || idx} className={idx % 2 === 0 ? "bg-gray-50" : "bg-white"}>
                <td className="p-3 border-b">{bus.registration_number}</td>
                <td className="p-3 border-b">{bus.capacity}</td>
                <td className="p-3 border-b">{bus.conductor ? bus.conductor.full_name : "N/A"}</td>
                <td className="p-3 border-b">
                  {bus.route ? `${bus.route.name} (${bus.route.start_point} → ${bus.route.end_point})` : "N/A"}
                </td>
                <td className="p-3 border-b text-center">
                  <button
                    onClick={() => handleViewTrips(bus.bus_id)}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded"
                  >
                    View Trips
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Optional Weather Info */}
      {weather.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mt-6 mb-2">Weather Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {weather.map((w, idx) => (
              <div key={idx} className="bg-gray-100 p-4 rounded shadow">
                <h3 className="font-semibold">{w.location}</h3>
                <p>{w.condition} — {w.temperature}°C</p>
                <p className="text-sm text-gray-600">{new Date(w.timestamp).toLocaleString()}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;