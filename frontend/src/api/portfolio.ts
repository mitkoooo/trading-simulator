import { API_BASE } from "../config/api";
import type { MePortfolioResponse } from "../types/api";
import type { Position } from "../types/domain";
import { mapToArray } from "../utils/utils";

export async function getPositions(): Promise<Position[]> {
  const res = await fetch(`${API_BASE}/me/portfolio`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  const data: MePortfolioResponse = await res.json();

  const arr = mapToArray(data.positions, "ticket") as Position[];

  console.log(arr);

  return arr;
}
