import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "./api";

function Login({ setToken }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const data = await login(email, password);
    setLoading(false);


    if (data.access) {
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      setToken(data.access);
      navigate("/dashboard");
    } else {
      setError(data.detail || data.error || "Login failed! Check your credentials.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-4">Login</h2>

      {error && <p className="text-red-500 mb-2">{error}</p>}

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="border p-2 mb-2 w-full"
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="border p-2 mb-2 w-full"
        required
      />
      <button
        type="submit"
        className="bg-blue-500 text-white px-4 py-2 rounded w-full"
        disabled={loading}
      >
        {loading ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}

export default Login;