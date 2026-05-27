import { useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Register({ onSwitch }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    try {
      await api.register(email, password);
      const data = await api.login(email, password);
      login(data.access_token);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-form">
      <h2>Create Account</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p className="error">{error}</p>}
        <button type="submit">Register</button>
      </form>
      <p>
        Already have an account?{" "}
        <button className="link" onClick={onSwitch}>
          Log in
        </button>
      </p>
    </div>
  );
}
