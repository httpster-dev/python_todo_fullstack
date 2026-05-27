import { useState } from "react";
import TodoForm from "./TodoForm";

export default function TodoItem({ todo, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false);

  async function handleUpdate(updates) {
    await onUpdate(todo.id, updates);
    setEditing(false);
  }

  async function toggleComplete() {
    await onUpdate(todo.id, { completed: !todo.completed });
  }

  function formatDate(iso) {
    if (!iso) return null;
    return new Date(iso).toLocaleString();
  }

  if (editing) {
    return (
      <li className="todo-item">
        <TodoForm
          initial={todo}
          onSubmit={handleUpdate}
          onCancel={() => setEditing(false)}
        />
      </li>
    );
  }

  return (
    <li className={`todo-item ${todo.completed ? "completed" : ""}`}>
      <div className="todo-main">
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={toggleComplete}
        />
        <div className="todo-text">
          <span className="todo-title">{todo.title}</span>
          {todo.description && (
            <span className="todo-desc">{todo.description}</span>
          )}
          {todo.due_date && (
            <span className="todo-due">Due: {formatDate(todo.due_date)}</span>
          )}
          {todo.reminder_scheduled && (
            <span className="badge">Reminder scheduled</span>
          )}
        </div>
      </div>
      <div className="todo-actions">
        <button onClick={() => setEditing(true)}>Edit</button>
        <button onClick={() => window.confirm("Delete this todo?") && onDelete(todo.id)}>Delete</button>
      </div>
    </li>
  );
}
