import { useEffect, useRef } from "react";
import { AlertTriangle } from "lucide-react";
import "../styles/ConfirmationDialog.css";
import Button from "./Button.jsx";

export default function ConfirmationDialog({
  isOpen,
  title = "Are you sure?",
  message,
  confirmLabel = "Deactivate",
  loadingLabel = "Deactivating...",
  cancelLabel = "Cancel",
  variant = "danger",
  isLoading = false,
  onConfirm,
  onCancel,
}) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen && !dialog.open) {
      dialog.showModal();
    } else if (!isOpen && dialog.open) {
      dialog.close();
    }
  }, [isOpen]);

  const handleCancel = (e) => {
    e.preventDefault();
    if (!isLoading) {
      onCancel?.();
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === dialogRef.current && !isLoading) {
      onCancel?.();
    }
  };

  return (
    <dialog
      ref={dialogRef}
      className="confirm-dialog"
      onCancel={handleCancel}
      onMouseDown={handleBackdropClick}
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-message"
    >
      <div className="confirm-dialog-body">
        <div className="confirm-dialog-header">
          <div className="confirm-dialog-icon" aria-hidden="true">
            <AlertTriangle size={22} />
          </div>

          <div className="confirm-dialog-text">
            <h2 id="confirm-dialog-title">{title}</h2>
            {message && <p id="confirm-dialog-message">{message}</p>}
          </div>
        </div>

        <div className="confirm-dialog-actions">
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            disabled={isLoading}
          >
            {cancelLabel}
          </Button>

          <Button
            type="button"
            variant={variant}
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? loadingLabel : confirmLabel}
          </Button>
        </div>
      </div>
    </dialog>
  );
}
