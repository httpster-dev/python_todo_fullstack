import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import "./App.css";

function AppContent() {
  const { token } = useAuth();
  const [view, setView] = useState("login");

  if (token) return <Dashboard />;

  return view === "login" ? (
    <Login onSwitch={() => setView("register")} />
  ) : (
    <Register onSwitch={() => setView("login")} />
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
