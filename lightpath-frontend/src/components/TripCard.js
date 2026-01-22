import React from "react";

const TripCard = ({ trip }) => {
  const {
    route_name,
    from,
    to,
    departure_time,
    fare,
    available_seats,
  } = trip;

  return (
    <div className="border rounded-lg p-4 shadow hover:shadow-lg transition cursor-pointer bg-white">
      <h3 className="font-semibold text-lg">{route_name}</h3>
      <p>
        <strong>From:</strong> {from} → <strong>To:</strong> {to}
      </p>
      <p>
        <strong>Departure:</strong>{" "}
        {new Date(departure_time).toLocaleString()}
      </p>
      <p>
        <strong>Fare:</strong> GHS {fare}
      </p>
      <p>
        <strong>Available Seats:</strong> {available_seats}
      </p>
    </div>
  );
};

export default TripCard;