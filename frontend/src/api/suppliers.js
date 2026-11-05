const API_URL = "http://localhost:8000";

export async function getAllSuppliers() {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    throw new Error("Authentication token not found. Please log in");
  }

  try {
    const response = await fetch(`${API_URL}/suppliers`, {
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

    return await response.json();
  } catch (error) {
    console.error("API error: ", error);
    throw error;
  }
}
