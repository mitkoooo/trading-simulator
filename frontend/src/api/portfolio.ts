import { API_BASE } from "../config/api";
import type { MePortfolioResponse } from "../types/api";
import type { Order, Portfolio } from "../types/domain";

export async function getPortfolio(): Promise<Portfolio> {
  const res = await fetch(`${API_BASE}/me/portfolio`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  const data: MePortfolioResponse = await res.json();

  return data;
}

export async function getPendingOrders(): Promise<Order[]> {
  try {
    const res = await fetch(`${API_BASE}/me/pending-orders`, {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      const errorData = await res.json();

      const errorMessage = errorData.detail || "Unknown error";
      throw Error(errorMessage);
    } else {
      const pendingOrders: Order[] = await res.json();
      return pendingOrders;
    }
  } catch (err: unknown) {
    console.error(err);
    throw err;
  }
}
