import { create } from "zustand";
import type { Stock } from "../types/domain";

interface StockViewDataState {
  selectedSymbol: string;
  selectedStock: Stock | null;

  setSelectedStock: (s: Stock) => void;
  setSelectedSymbol: (sym: string) => void;
}

export const useStockViewDataStore = create<StockViewDataState>((set) => ({
  selectedSymbol: "",
  selectedStock: null,
  setSelectedStock: (s) => set(() => ({ selectedStock: s })),
  setSelectedSymbol: (sym) => set(() => ({ selectedSymbol: sym })),
}));
