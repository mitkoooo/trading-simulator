import { API_BASE } from "../config/api";
import type { MePortfolioResponse } from "../types/api";
import type { Portfolio, Position } from "../types/domain";
import { mapToArray } from "../utils/utils";

export async function getPortfolio(): Promise<Portfolio> {
  const res = await fetch(`${API_BASE}/me/portfolio`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  const data: MePortfolioResponse = await res.json();

  const arr = mapToArray(data.portfolio.positions, "ticket") as Position[];

  return {
    positions: arr,
    cash: data.portfolio.cash,
    value: data.portfolio.value,
  };
}
