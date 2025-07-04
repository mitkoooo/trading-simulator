import { API_BASE } from "../config/api";

export async function getMatchOrders() {
  try {
    const res = await fetch(`${API_BASE}/match-orders`, {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      throw new Error(`Couldn't fetch the market data (${res.status})`);
    }

    return;
  } catch (err: unknown) {
    console.error(err);
    throw err;
  }
}
