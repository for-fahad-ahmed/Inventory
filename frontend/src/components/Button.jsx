import "../styles/Button.css";

export default function Button({
  children,
  type = "button",
  onClick,
  variant = "primary",
  className = "btn",
  ...props
}) {
  const buttonClass = `${className} btn-${variant}`.trim();

  return (
    <button type={type} onClick={onClick} className={buttonClass} {...props}>
      {children}
    </button>
  );
}
