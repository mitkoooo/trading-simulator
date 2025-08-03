import { API_BASE } from "../config/api";
import type { MeResponse } from "../types/api";

export async function isAuthenticated(): Promise<boolean> {
  const resp = await fetch(`${API_BASE}/users/me`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  return resp.ok;
}

export async function getTraderId(): Promise<string> {
  try {
    const res = await fetch(`${API_BASE}/users/me`, {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      throw new Error(`Not authenticated (${res.status})`);
    }

    const data: MeResponse = await res.json();

    return data.trader_id;
  } catch (err: unknown) {
    console.error(err);
    throw err;
  }
}
