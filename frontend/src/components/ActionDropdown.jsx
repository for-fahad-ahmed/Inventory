import { Fragment, useEffect, useRef, useState } from "react";
import { MoreVertical } from "lucide-react";
import "../styles/ActionDropdown.css";

export default function ActionDropdown({ actions = [] }) {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === "Escape" && open) {
        setOpen(false);
      }
    };

    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [open]);

  const handleAction = (action) => {
    setOpen(false);
    action.onClick?.();
  };

  return (
    <div className="action-dropdown-wrapper" ref={dropdownRef}>
      <button
        type="button"
        className="action-dropdown-trigger"
        onClick={() => setOpen((prev) => !prev)}
      >
        <MoreVertical size={20} />
      </button>

      {open && actions.length > 0 && (
        <div className="action-dropdown-menu" role="menu">
          {actions.map((action) => (
            <Fragment key={action.label}>
              {action.divider && <div className="action-dropdown-divider" />}

              <button
                type="button"
                role="menuitem"
                className={`action-dropdown-item ${
                  action.danger ? "danger" : ""
                }`}
                onClick={() => handleAction(action)}
              >
                {action.icon}
                <span>{action.label}</span>
              </button>
            </Fragment>
          ))}
        </div>
      )}
    </div>
  );
}
