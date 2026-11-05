import "../styles/Button.css";

export default function Button({
  children,
  type = "button",
  onClick,
  className = "btn",
  ...props
}) {
  return (
    <button type={type} onClick={onClick} className={className} {...props}>
      {children}
    </button>
  );
}
