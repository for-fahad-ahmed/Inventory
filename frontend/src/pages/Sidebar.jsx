import { useState, useEffect } from "react";
import { NavLink, useNavigate } from "react-router-dom";

import "../styles/Sidebar.css";
import { getCurrentUser } from "../api/auth";

const tabs = [
  { label: "Dashboard", path: "/dashboard", icon: "" },
  { label: "Products", path: "/products", icon: "" },
  { label: "Inventory", path: "/inventory", icon: "" },
  { label: "Purchases", path: "/purchases", icon: "" },
  { label: "Sales", path: "/sales", icon: "" },
  { label: "Suppliers", path: "/suppliers", icon: "" },
  { label: "Customers", path: "/customers", icon: "" },
  { label: "Users & Settings", path: "/settings", icon: "" },
];

export default function Sidebar() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;

    async function loadUser() {
      try {
        const data = await getCurrentUser(
          sessionStorage.getItem("access_token"),
        );

        if (active) {
          setUser(data);
        }
      } catch (error) {
        console.error("Failed to load user profile:", error);
        if (error.status === 401) {
          sessionStorage.clear();
          navigate("/login", { replace: true });
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadUser();

    return () => {
      active = false;
    };
  }, [navigate]);

  const displayName = user?.name || user?.username || "User";

  const initials = displayName
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  function handleLogout() {
    sessionStorage.clear();
    navigate("/login", { replace: true });
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span>Peripherals</span>
      </div>

      <nav className="sidebar-nav" aria-label="Main navigation">
        <ul className="tabs">
          {tabs.map((tab) => (
            <li key={tab.path}>
              <NavLink
                to={tab.path}
                className={({ isActive }) => `tab${isActive ? " active" : ""}`}
              >
                {tab.icon && (
                  <img
                    src={tab.icon}
                    width="25"
                    height="25"
                    alt=""
                    aria-hidden="true"
                  />
                )}
                <span>{tab.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-profile">
        <div className="profile-avatar" aria-hidden="true">
          {initials || "U"}
        </div>
        <div className="profile-details">
          <span className="profile-name" title={displayName}>
            {displayName}
          </span>

          <span className="profile-email" title={user?.email || ""}>
            {loading ? "Loading profile..." : user?.email || ""}
          </span>
        </div>
      </div>

      <button type="button" className="sidebar-logout" onClick={handleLogout}>
        Log out
      </button>
    </aside>
  );
}
