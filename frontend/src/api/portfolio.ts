import { API_BASE } from "../config/api";
import type { PortfolioResponse } from "../types/api";
import type { Order, OrderInfo } from "../types/domain";

export interface GetOrderHistoryResponse {
  history: OrderInfo[];
}

export interface GetOrdersResponse {
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

  const data: PortfolioResponse = await res.json();

  return data;
}

export async function getOrderHistory(
  trader_id: string,
): Promise<GetOrderHistoryResponse | undefined> {
  try {
    const res = await fetch(`${API_BASE}/users/${trader_id}/orders/history`, {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      const errorData = await res.json();

      const errorMessage = errorData.detail || "Unknown error";
      throw Error(errorMessage);
    } else {
      const result: GetOrderHistoryResponse = await res.json();
      return result;
    }
  } catch (err: unknown) {
    console.error(err);
  }
}

export async function getOrders(
  trader_id: string,
  status: string,
): Promise<GetOrdersResponse | undefined> {
  try {
    const res = await fetch(
      `${API_BASE}/users/${trader_id}/orders?status=${status}`,
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
      const result: GetOrdersResponse = await res.json();
      return result;
    }
  } catch (err: unknown) {
    console.error(err);
  }
}
