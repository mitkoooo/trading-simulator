import { API_BASE } from "../config/api";
import type { PortfolioResponse } from "../types/api";
import type { Order, Portfolio } from "../types/domain";

export interface GetPendingOrdersResponse {
  status: number;
  orders: Order[];
}

export async function getPortfolio(
  trader_id: string,
): Promise<PortfolioResponse> {
  const res = await fetch(`${API_BASE}/users/${trader_id}/portfolio`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  const data: MePortfolioResponse = await res.json();

  return data;
}

export async function getPendingOrders(
  trader_id: string,
): Promise<GetPendingOrdersResponse> {
  try {
    const res = await fetch(
      `${API_BASE}/users/${trader_id}/orders?status=pending`,
      {
        method: "GET",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      },
    );

    if (!res.ok) {
      const errorData = await res.json();

      const errorMessage = errorData.detail || "Unknown error";
      throw Error(errorMessage);
    } else {
      const result: GetPendingOrdersResponse = await res.json();
      return result;
    }
  } catch (err: unknown) {
    console.error(err);
    throw err;
  }
}
