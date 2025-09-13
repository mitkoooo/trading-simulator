import { create } from "zustand";
import type { Quote } from "../types/domain";

export interface DailySummary {
  symbol: string;
  open: number;
  previousClosed: number;
}

interface MarketDataState {
  quotes: Record<string, Quote>;
  dailySummaries: Record<string, DailySummary>;

  upsertSummary: (summary: DailySummary) => void;
  upsertQuote: (q: Quote) => void;

  upsertQuotes: (qs: Quote[]) => void;
  upsertSummaries: (ss: DailySummary[]) => void;
}

export const useMarketDataStore = create<MarketDataState>((set) => ({
  quotes: {},
  dailySummaries: {},
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
