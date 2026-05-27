function formatLocalTime(isoString) {
  return new Date(isoString).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function Notifications({ notifications, onMarkRead }) {
  const unread = notifications.filter((n) => n.status === "sent");

  if (!unread.length) return null;

  return (
    <div className="notifications">
      <h3>Notifications</h3>
      <ul>
        {unread.map((n) => (
          <li key={n.id} className="notification-item">
            <div className="notif-body">
              <span className="notif-message">{n.message}</span>
              {n.due_date && (
                <span className="notif-due">{formatLocalTime(n.due_date)}</span>
              )}
              <span className="notif-time">
                Received {formatLocalTime(n.created_at)}
              </span>
            </div>
            <button
              className="dismiss-btn"
              aria-label={`Dismiss: ${n.message}`}
              onClick={() => onMarkRead(n.id)}
            >
              Dismiss
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
