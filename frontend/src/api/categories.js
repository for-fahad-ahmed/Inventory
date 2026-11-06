const API_URL = "http://localhost:8000";

export async function getAllCategories() {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    throw new Error("Authentication token not found. Please log in");
  }

  try {
    const response = await fetch(`${API_URL}/categories`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();

      if (response.status === 401) {
        sessionStorage.clear();
        window.location.replace("/login");
        throw new Error("Session expired. Please log in again.");
      }

      if (response.status == 403) {
        throw new Error("You don't have permission to access categories.");
      }
      throw new Error(
        `HTTP ${response.status}: ${errorText || response.statusText}`,
      );
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching categories: ", error);
    throw error;
  }
}
