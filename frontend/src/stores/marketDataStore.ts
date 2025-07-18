import { create } from "zustand";
import { getMarketData, nextTick } from "../api/marketdata";
import type { Stock } from "../types/domain";

type MarketDataStore = {
	marketData: null | Map<string, Stock>;
	fetchNextMarketData: () => Promise<void>;
	fetchMarketData: () => Promise<void>;
	getMarketPrice: (symbol: string) => Stock | null;
};

export const useMarketDataStore = create<MarketDataStore>((set, get) => {
	// shared load
	const load = async (loader: () => Promise<Stock[]>) => {
		const data = await loader();
		const map = new Map<string, Stock>(data.map((s) => [s.symbol, s]));
		set({ marketData: map });
	};

	return {
		marketData: null,
		fetchMarketData: () => load(getMarketData),
		fetchNextMarketData: () => load(nextTick),
		getMarketPrice: (symbol: string): Stock | null => {
			const md = get().marketData;
			return md?.get(symbol) ?? null;
		},
	};
});
