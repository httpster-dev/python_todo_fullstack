const BASE = "http://localhost:8000";

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return null;

  const data = await res.json();
  if (!res.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map((e) => e.msg).join(", ")
      : detail || "Request failed";
    throw new Error(message);
  }
  return data;
}

export const api = {
  register: (email, password) =>
    request("POST", "/api/auth/register", { email, password }),

  login: (email, password) =>
    request("POST", "/api/auth/login", { email, password }),

  getTodos: () => request("GET", "/api/todos"),

  createTodo: (todo) => request("POST", "/api/todos", todo),

  updateTodo: (id, updates) => request("PUT", `/api/todos/${id}`, updates),

  deleteTodo: (id) => request("DELETE", `/api/todos/${id}`),

  getNotifications: () => request("GET", "/api/notifications"),

  markNotificationRead: (id) => request("PATCH", `/api/notifications/${id}/read`),
};
