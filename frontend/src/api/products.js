const API_URL = "http://localhost:8000";

export async function CreateProduct(product) {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    throw new Error("Authentication token not found. Please log in.");
  }

  const response = await fetch(`${API_URL}/products/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(product),
  });

  if (!response.ok) {
    if (response.status === 401) {
      sessionStorage.clear();
      window.location.replace("/login");
      throw new Error("Session expired. Please log in again.");
    }

    if (response.status === 403) {
      throw new Error("You don't have permission to create products.");
    }

    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to create product (${response.status})`,
    );
  }

  return response.json();
}

export async function DeactivateProduct(productId) {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    throw new Error("Authentication token not found. Please log in.");
  }

  const response = await fetch(`${API_URL}/products/${productId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      sessionStorage.clear();
      window.location.replace("/login");
      throw new Error("Session expired. Please log in again.");
    }

    if (response.status === 403) {
      throw new Error("You don't have permission to deactivate products.");
    }

    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to deactivate product (${response.status})`,
    );
  }

  return true;
}
