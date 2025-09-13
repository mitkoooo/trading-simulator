import { API_BASE } from "../config/api";
import type { DailySummary } from "../stores/marketDataStore";

interface GetDailySummaryResponse {
  summaries: DailySummary[];
}

export async function getDailySummaries() {
  const res = await fetch(`${API_BASE}/market-data/daily-summary/bulk`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  const data: GetDailySummaryResponse = await res.json();

  console.log(data);

  return data;
}
