import { API_BASE } from "../config/api";
import type { DailySummary } from "../stores/marketDataStore";
import type { Stock } from "../types/domain";

interface GetDailySummaryResponse {
  summaries: DailySummary[];
}

interface GetStocksResponse {
  stocks: Stock[];
}

export async function getDailySummaries() {
  const res = await fetch(`${API_BASE}/market-data/daily-summary/bulk`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  const data: GetDailySummaryResponse = await res.json();

  return data;
}

export async function getStocks() {
  const res = await fetch(`${API_BASE}/market-data/stocks`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  const data: GetStocksResponse = await res.json();

  console.log(data);

  return data;
}
