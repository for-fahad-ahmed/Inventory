import { useEffect } from "react";
import "../styles/Toast.css";

export default function Toast({
  message,
  type = "success",
  duration = 3500,
  onClose,
}) {
  let icon;

  if (type === "success") {
    icon = "✓";
  } else if (type === "warning") {
    icon = "⚠";
  } else if (type === "info") {
    icon = "ℹ";
  } else if (type === "error") {
    icon = "✕";
  } else {
    icon = "•";
  }

  useEffect(() => {
    if (!duration || !onClose) return;

    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  if (!message) return null;

  return (
    <div
      className={`toast-container toast-${type}`}
      role={type === "error" ? "alert" : "status"}
      aria-live="polite"
    >
      <span className="toast-icon" aria-hidden="true">
        {icon}
      </span>
      <span className="toast-message">{message}</span>

      {onClose && (
        <button
          type="button"
          className="toast-close"
          onClick={onClose}
          aria-label="Close"
        >
          &times;
        </button>
      )}
    </div>
  );
}
