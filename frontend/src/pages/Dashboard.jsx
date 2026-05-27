import { useEffect, useState, useCallback } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import TodoForm from "../components/TodoForm";
import TodoItem from "../components/TodoItem";
import Notifications from "../components/Notifications";

export default function Dashboard() {
  const { logout } = useAuth();
  const [todos, setTodos] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState(null);

  const fetchAll = useCallback(async () => {
    try {
      const [t, n] = await Promise.all([api.getTodos(), api.getNotifications()]);
      setTodos(t);
      setNotifications(n);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    // Poll for new notifications every 10 seconds (reminder jobs fire async)
    const interval = setInterval(fetchAll, 10000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  async function handleCreate(todoData) {
    await api.createTodo(todoData);
    await fetchAll();
  }

  async function handleUpdate(id, updates) {
    await api.updateTodo(id, updates);
    await fetchAll();
  }

  async function handleDelete(id) {
    await api.deleteTodo(id);
    await fetchAll();
  }

  return (
    <div className="dashboard">
      <header>
        <h1>My Todos</h1>
        <button onClick={logout}>Log Out</button>
      </header>

      {error && <p className="error">{error}</p>}

      <section>
        <h2>Add Todo</h2>
        <TodoForm onSubmit={handleCreate} />
      </section>

      <section>
        <h2>Todos</h2>
        {todos.length === 0 ? (
          <p>No todos yet.</p>
        ) : (
          <ul className="todo-list">
            {todos.map((todo) => (
              <TodoItem
                key={todo.id}
                todo={todo}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
              />
            ))}
          </ul>
        )}
      </section>

      <Notifications notifications={notifications} />
    </div>
  );
}
