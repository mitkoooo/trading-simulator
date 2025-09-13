import { create } from "zustand";
import type { Order, OrderInfo, Portfolio } from "../types/domain";
import { getOrderHistory, getOrders, getPortfolio } from "../api/portfolio";
import type { PortfolioResponse } from "../types/api";
import { getTraderId } from "../api/auth";

interface PortfolioDataStore {
  traderId: string | null;
  portfolio: Portfolio;
  orderHistory: Record<string, OrderInfo>;
  pendingOrders: Record<string, Order>;
  fetchTraderId: () => Promise<string>;
  fetchPortfolioData: () => Promise<void>;
  upsertOrderHistory: () => Promise<void>;
  fetchPendingOrders: () => Promise<void>;
}

export const usePortfolioDataStore = create<PortfolioDataStore>((set, get) => ({
  traderId: null,
  portfolio: {
    positions: [],
    cash: 0,
    value: 0,
    realizedPnL: 0,
  },
  orderHistory: {},
  pendingOrders: {},

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
        realizedPnL: pRes.realized_pnl,
        value: pRes.value,
      },
    });
  },
  upsertOrderHistory: async () => {
    if (!get().traderId) {
      await get().fetchTraderId();
    }
    const traderId = get().traderId;
    if (!traderId) return;
    const newData = await getOrderHistory(traderId);
    const orderHistory = newData.history;

    set((s) => {
      if (!orderHistory.length) return s;
      const next = { ...s.orderHistory };
      let changed = false;
      for (const order of orderHistory) {
        const prev = next[order.order_id];
        if (
          !prev ||
          prev.avg_fill_price !== order.avg_fill_price ||
          prev.status !== order.status ||
          prev.fill_qty !== order.fill_qty
        ) {
          next[order.order_id] = order;
          changed = true;
        }
      }

      return changed ? { orderHistory: next } : s;
    });
  },
  fetchPendingOrders: async () => {
    if (!get().traderId) {
      await get().fetchTraderId();
    }
    const traderId = get().traderId;
    if (!traderId) return;
    const newData = await getOrders(traderId, "pending");
    const pendingOrders = newData.orders;

    set((s) => {
      const next: Record<string, Order> = {};

      // Fill new data
      for (const order of pendingOrders) {
        next[order.order_id] = order;
      }

      // Compare with existing
      const changed =
        Object.keys(next).length !== Object.keys(s.pendingOrders).length ||
        Object.keys(next).some((id) => {
          const prev = s.pendingOrders[id];
          const curr = next[id];
          return (
            !prev ||
            prev.limit_price !== curr.limit_price ||
            prev.status !== curr.status ||
            prev.quantity !== curr.quantity
          );
        });

      return changed ? { pendingOrders: next } : s;
    });
  },
}));
