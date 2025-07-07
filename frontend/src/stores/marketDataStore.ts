import { create } from "zustand";
import { nextTick } from "../api/marketdata";
import type { Stock } from "../types/domain";

type MarketDataStore = {
  marketData: null | Stock[];
  fetchNextMarketData: () => Promise<void>;
};

export const useMarketDataStore = create<MarketDataStore>((set) => ({
  marketData: null,
  fetchNextMarketData: async () => {
    const newMarketData = await nextTick();
    set({ marketData: newMarketData });
  },
}));
