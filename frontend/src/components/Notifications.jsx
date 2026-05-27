export default function Notifications({ notifications, onMarkRead }) {
  const unread = notifications.filter((n) => n.status === "sent");

  if (!unread.length) return null;

  return (
    <div className="notifications">
      <h3>Notifications</h3>
      <ul>
        {unread.map((n) => (
          <li key={n.id} className="notification-item">
            <span>{n.message}</span>
            <span className="notif-time">
              {new Date(n.created_at).toLocaleString()}
            </span>
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
