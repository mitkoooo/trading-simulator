import { API_BASE } from "../config/api";
import type { MePortfolioResponse } from "../types/api";
import type { Portfolio } from "../types/domain";

export async function getPortfolio(): Promise<Portfolio> {
  const res = await fetch(`${API_BASE}/me/portfolio`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  const data: MePortfolioResponse = await res.json();

  return data;
}
