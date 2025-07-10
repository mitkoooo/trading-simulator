import { create } from "zustand";
import { getMarketData, nextTick } from "../api/marketdata";
import type { Stock } from "../types/domain";

type MarketDataStore = {
  marketData: null | Stock[];
  fetchNextMarketData: () => Promise<void>;
  fetchMarketData: () => Promise<void>;
};

export const useMarketDataStore = create<MarketDataStore>((set) => ({
  marketData: null,
  fetchMarketData: async () => {
    const newMarketData = await getMarketData();
    set({ marketData: newMarketData });
  },
  fetchNextMarketData: async () => {
    const newMarketData = await nextTick();
    set({ marketData: newMarketData });
  },
}));
