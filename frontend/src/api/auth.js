const API_URL = "http://localhost:8000";

export async function loginUser(username, password) {
  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);

  const response = await fetch(`${API_URL}/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }
  return data;
}

export async function getCurrentUser(accessToken) {
  if (!accessToken) {
    const err = new Error("Authentication token not found. Please log in");
    err.status = 401;
    throw err;
  }

  const response = await fetch(`${API_URL}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const err = new Error(data.detail || "Could not fetch user");
    err.status = response.status;
    throw err;
  }

  return data;
}
