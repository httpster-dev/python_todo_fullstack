import { useState } from "react";

export default function TodoForm({ onSubmit, initial = {}, onCancel }) {
  const [title, setTitle] = useState(initial.title || "");
  const [description, setDescription] = useState(initial.description || "");
  const [dueDate, setDueDate] = useState(
    initial.due_date ? initial.due_date.slice(0, 10) : ""
  );
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    try {
      await onSubmit({
        title,
        description: description || null,
        due_date: dueDate ? new Date(dueDate + 'T00:00:00Z').toISOString() : null,
      });
      if (!initial.id) {
        setTitle("");
        setDescription("");
        setDueDate("");
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="todo-form">
      <input
        type="text"
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <input
        type="text"
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <input
        type="date"
        value={dueDate}
        onChange={(e) => setDueDate(e.target.value)}
      />
      {error && <p className="error">{error}</p>}
      <div className="form-actions">
        <button type="submit">{initial.id ? "Save" : "Add Todo"}</button>
        {onCancel && (
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
