import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Login.css";
import Button from "../components/Button.jsx";
import { loginUser } from "../api/auth.js";

export default function Login() {
  const navigate = useNavigate();

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const formData = new FormData(e.target);
    const username = formData.get("username");
    const password = formData.get("password");

    try {
      const data = await loginUser(username, password);

      if (!data?.access_token) {
        throw new Error("Invalid login response");
      }

      sessionStorage.setItem("access_token", data.access_token);

      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="login-page">
      <div className="left-sidebar"></div>
      <div className="main">
        <h1>Login</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            id="username"
            name="username"
            required
            minLength={1}
            maxLength={20}
            placeholder="Username"
            disabled={loading}
          />

          <input
            type="password"
            id="password"
            name="password"
            required
            minLength={8}
            maxLength={255}
            placeholder="Password"
            disabled={loading}
          />

          {error && (
            <p className="error-message" role="alert">
              {error}
            </p>
          )}

          <Button type="submit" className="btn" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </Button>
        </form>
      </div>
    </div>
  );
}
