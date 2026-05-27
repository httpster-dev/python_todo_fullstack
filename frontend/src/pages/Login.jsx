import { useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Login({ onSwitch }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    try {
      const data = await api.login(email, password);
      login(data.access_token);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-form">
      <h2>Log In</h2>
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
        <button type="submit">Log In</button>
      </form>
      <p>
        No account?{" "}
        <button className="link" onClick={onSwitch}>
          Register
        </button>
      </p>
    </div>
  );
}
