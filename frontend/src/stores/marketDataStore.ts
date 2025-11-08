import { create } from "zustand";
import type { Quote, Stock } from "../types/domain";

export interface DailySummary {
  symbol: string;
  open: number;
  previousClosed: number;
}

interface MarketDataState {
  stocks: Record<string, Stock>;
  quotes: Record<string, Quote>;
  dailySummaries: Record<string, DailySummary>;

  setStocks: (ss: Stock[]) => void;
  upsertSummary: (summary: DailySummary) => void;
  upsertQuote: (q: Quote) => void;

  upsertQuotes: (qs: Quote[]) => void;
  upsertSummaries: (ss: DailySummary[]) => void;
}

export const useMarketDataStore = create<MarketDataState>((set) => ({
  stocks: {},
  quotes: {},
  dailySummaries: {},
  setStocks: (ss) =>
    set((s) => {
      for (const stock of ss) {
        s.stocks[stock.symbol] = stock;
      }
      return s;
    }),
  upsertQuote: (q) => set((s) => ({ quotes: { ...s.quotes, [q.symbol]: q } })),
  upsertSummary: (summ) =>
    set((s) => ({
      dailySummaries: { ...s.dailySummaries, [summ.symbol]: summ },
    })),
  upsertQuotes: (qs) =>
    set((s) => {
      if (!qs.length) return s;
      const next = { ...s.quotes };
      let changed = false;
      for (const q of qs) {
        const prev = next[q.symbol];
        if (
          !prev ||
          prev.bidPrice !== q.bidPrice ||
          prev.askPrice !== q.askPrice ||
          prev.lastPrice !== q.lastPrice ||
          prev.bidSize !== q.bidSize ||
          prev.askSize !== q.askSize
        ) {
          next[q.symbol] = q;
          changed = true;
        }
      }
      return changed ? { quotes: next } : s;
    }),
  upsertSummaries: (summs) =>
    set((s) => {
      if (!summs.length) return s;
      const next = { ...s.dailySummaries };
      let changed = false;
      for (const summ of summs) {
        const prev = next[summ.symbol];
        if (
          !prev ||
          prev.open !== summ.open ||
          prev.previousClosed !== summ.previousClosed
        ) {
          next[summ.symbol] = summ;
          changed = true;
        }
      }
      return changed ? { dailySummaries: next } : s;
    }),
}));
