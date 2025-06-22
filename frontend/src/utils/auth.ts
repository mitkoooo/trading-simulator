const API: string = "http://localhost:8000";

export async function isAuthenticated(): Promise<boolean> {
  const resp = await fetch(`${API}/me`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  return resp.ok;
}
