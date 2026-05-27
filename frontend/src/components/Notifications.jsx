export default function Notifications({ notifications }) {
  if (!notifications.length) return null;

  return (
    <div className="notifications">
      <h3>Notifications</h3>
      <ul>
        {notifications.map((n) => (
          <li key={n.id} className="notification-item">
            <span>{n.message}</span>
            <span className="notif-time">
              {new Date(n.created_at).toLocaleString()}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
