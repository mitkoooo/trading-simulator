import { create } from "zustand";
import type { Order, Portfolio } from "../types/domain";
import { getPendingOrders, getPortfolio } from "../api/portfolio";
import type { MePortfolioResponse } from "../types/api";

interface PortfolioDataStore {
  portfolio: Portfolio;
  pendingOrders: Order[];
  fetchPortfolioData: () => Promise<void>;
  fetchPendingOrders: () => Promise<void>;
}

export const usePortfolioDataStore = create<PortfolioDataStore>((set) => ({
  portfolio: {
    positions: [],
    cash: 0,
    value: 0,
    totalPnL: 0,
  },
  pendingOrders: [],
  fetchPortfolioData: async () => {
    const newPortfolioData: MePortfolioResponse = await getPortfolio();
    set({ portfolio: { ...newPortfolioData } });
  },
  fetchPendingOrders: async () => {
    const newPendingOrders = await getPendingOrders();
    set({ pendingOrders: newPendingOrders });
  },
}));
