import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Login from "./Login";
import TripsPage from "./pages/TripsPage";

function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token"));

  // Keep token in sync with localStorage (in case of refresh)
  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (storedToken !== token) setToken(storedToken);
  }, [token]);

  // PrivateRoute helper
  const PrivateRoute = ({ children }) => {
    return token ? children : <Navigate to="/login" replace />;
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login setToken={setToken} />} />

        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />

        <Route
          path="/trips/:busId"
          element={
            <PrivateRoute>
              <TripsPage />
            </PrivateRoute>
          }
        />

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

export default App;