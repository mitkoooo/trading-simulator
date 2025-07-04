import { API_BASE } from "../config/api";
import type { MarketDataResponse } from "../types/api";
import type { Stock } from "../types/domain";
import { mapToArray } from "../utils/utils";

export async function getMarketData(): Promise<Array<Stock>> {
  try {
    const res = await fetch(`${API_BASE}/market-data`, {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      throw new Error(`Couldn't fetch the market data (${res.status})`);
    }

    const data: MarketDataResponse = await res.json();

    const arr = mapToArray(data.market_data, "symbol");

    return arr;
  } catch (err: unknown) {
    console.error(err);
    throw err;
  }
}

export async function nextTick(): Promise<Stock[]> {
  try {
    const res = await fetch(`${API_BASE}/market-data/next`, {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      throw new Error(`Couldn't advance the market data (${res.status})`);
    }

    const data: MarketDataResponse = await res.json();

    const arr = mapToArray(data.market_data, "symbol");

    return arr;
  } catch (err) {
    console.error(err);
    throw err;
  }
}
