import { create } from "zustand";

export interface Quote {
	symbol: string;
	bid_price: number | null;
	bid_size: number | null;
	ask_price: number | null;
	ask_size: number | null;
	last: number | null;
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
