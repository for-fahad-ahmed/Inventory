import "../styles/PageHeader.css";
import Button from "./Button.jsx";

export default function PageHeader({
  title,
  subtitle,
  actionLabel,
  onAction,
  children,
}) {
  return (
    <div className="page-header-card">
      <div className="page-header-top">
        <div className="page-header-text">
          <h1>{title}</h1>
          {subtitle && <p>{subtitle}</p>}
        </div>

        {actionLabel && (
          <Button type="button" onClick={onAction}>
            {actionLabel}
          </Button>
        )}
      </div>

      {children && <div className="page-header-body">{children}</div>}
    </div>
  );
}
