import { create } from "zustand";
import type { Order, Portfolio } from "../types/domain";
import { getPendingOrders, getPortfolio } from "../api/portfolio";
import type { PortfolioResponse } from "../types/api";
import { getTraderId } from "../api/auth";

interface PortfolioDataStore {
  traderId: string | null;
  portfolio: Portfolio;
  pendingOrders: Order[];
  fetchTraderId: () => Promise<string>;
  fetchPortfolioData: () => Promise<void>;
  fetchPendingOrders: () => Promise<void>;
}

export const usePortfolioDataStore = create<PortfolioDataStore>((set, get) => ({
  traderId: null,
  portfolio: {
    positions: [],
    cash: 0,
    value: 0,
    totalPnL: 0,
  },
  pendingOrders: [],

  fetchTraderId: async () => {
    const traderId = await getTraderId();
    set({ traderId: traderId });
    return traderId;
  },
  fetchPortfolioData: async () => {
    if (!get().traderId) {
      await get().fetchTraderId();
    }

    const traderId = get().traderId;

    if (!traderId) return;

    const pRes: PortfolioResponse = await getPortfolio(traderId);
    set({
      portfolio: {
        cash: pRes.cash,
        positions: pRes.positions,
        totalPnL: pRes.total_pnl,
        value: pRes.value,
      },
    });
  },
  fetchPendingOrders: async () => {
    if (!get().traderId) {
      await get().fetchTraderId();
    }
    const traderId = get().traderId;
    if (!traderId) return;
    const newData = await getPendingOrders(traderId);
    const newPendingOrders = newData.orders;
    set({ pendingOrders: newPendingOrders });
  },
}));
