import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getTrips } from "../api";
import TripCard from "../components/TripCard";

const TripsPage = () => {
  const { busId } = useParams();
  const navigate = useNavigate();

  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTripsForBus = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getTrips(busId);
        if (data.error) throw new Error(data.error);
        setTrips(Array.isArray(data) ? data : data.results);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTripsForBus();
  }, [busId]);

  const handleTripClick = (tripId) => {
    navigate(`/trip/${tripId}`);
  };

  if (loading) return <p className="p-6 text-gray-500">Loading trips...</p>;
  if (error) return <p className="p-6 text-red-500">{error}</p>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-blue-700">
        Trips for Bus {busId}
      </h1>

      {trips.length === 0 ? (
        <p className="text-gray-600">No trips available for this bus.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {trips.map((trip) => (
            <div
              key={trip.id}
              className="cursor-pointer"
              onClick={() => handleTripClick(trip.id)}
            >
              <TripCard
                trip={{
                  route_name: trip.route?.name || "N/A",
                  from: trip.route?.start_point || "N/A",
                  to: trip.route?.end_point || "N/A",
                  departure_time: trip.departure_time,
                  fare: trip.fare,
                  available_seats: trip.available_seats,
                }}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TripsPage;