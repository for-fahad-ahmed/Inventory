const API_URL = "http://localhost:8000";

export async function getLowStockProducts() {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    throw new Error("Authentication token not found. Please log in");
  }
  try {
    const response = await fetch(`${API_URL}/inventory/?low_stock=true`, {
      method: "GET",
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
      const error = await response.text();
      throw new Error(`HTTP ${response.status}: ${error}`);
    }

    const data = await response.json();
    return Array.isArray(data?.products) ? data.products : [];
  } catch (error) {
    console.error("Low stock API error:", error);
    throw error;
  }
}

export async function getInventory(
  limit = null,
  skip = null,
  active_only = true,
  category_id = null,
  supplier_id = null,
  low_stock = false,
  search = "",
) {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    throw new Error("Authentication token not found. Please log in.");
  }
  const params = new URLSearchParams();

  if (limit != null) params.append("limit", limit);
  if (skip !== null) params.append("skip", skip);

  params.append("active_only", active_only);
  params.append("low_stock", low_stock);
  if (category_id !== null && category_id !== "") {
    params.append("category_id", category_id);
  }

  if (supplier_id !== null && supplier_id !== "") {
    params.append("supplier_id", supplier_id);
  }

  if (search.trim()) {
    params.append("search", search.trim());
  }
  try {
    const response = await fetch(`${API_URL}/inventory/?${params.toString()}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        sessionStorage.clear();
        window.location.replace("/login");
        throw new Error("Session expired. Please log in again");
      }
      const error = await response.text();
      throw new Error(`HTTP ${response.status}: ${error}`);
    }

    const data = await response.json();
    return {
      products: Array.isArray(data?.products) ? data.products : [],
      total: data?.total ?? 0,
      skip: data?.skip ?? 0,
      limit: data?.limit ?? 10,
      has_more: Boolean(data?.has_more),
    };
  } catch (error) {
    console.error("API error", error);
    throw error;
  }
}
