import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { useStockViewDataStore } from "../stores/stockViewDataStore";
import { API_BASE } from "../config/api";
import type { Stock } from "../types/domain";

async function fetchStock(symbol: string): Promise<Stock> {
  const res = await fetch(`${API_BASE}/market-data/stocks/${symbol}`);
  if (!res.ok) throw new Error("Network error");
  const data = await res.json();
  console.log(data);
  return data.stock;
}

export function useStock() {
  const selectedSymbol = useStockViewDataStore((s) => s.selectedSymbol);
  const symbol = selectedSymbol ?? "";
  const setSelectedStock = useStockViewDataStore((s) => s.setSelectedStock);

  const query = useQuery<Stock, Error>({
    queryKey: ["stock", symbol],
    queryFn: () => fetchStock(symbol),
    refetchInterval: 1000,
    staleTime: 500,
    enabled: !!selectedSymbol,
  });

  useEffect(() => {
    if (query.data) {
      setSelectedStock(query.data);
    }
  }, [query.data, setSelectedStock]);

  return query;
}
