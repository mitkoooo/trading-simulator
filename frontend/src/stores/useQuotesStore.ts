import { create } from "zustand";

export interface Quote {
  symbol: string;
  bidPrice: number | null;
  bidSize: number | null;
  askPrice: number | null;
  askSize: number | null;
  lastPrice: number | null;
  timestamp: Date;
}

interface QuotesState {
  quotes: Quote[];
  setQuotes: (qs: Quote[]) => void;
}

export const useQuotesStore = create<QuotesState>((set) => ({
  quotes: [],
  setQuotes: (qs) => set({ quotes: qs }),
}));
