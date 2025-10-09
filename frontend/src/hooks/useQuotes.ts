import { useQuery } from "@tanstack/react-query";
import { API_BASE } from "../config/api";
import { useMarketDataStore } from "../stores/marketDataStore";
import { useEffect } from "react";
import type { Quote } from "../types/domain";

export interface QuoteDTO {
  symbol: string;
  bid_price: number | null;
  bid_size: number | null;
  ask_price: number | null;
  ask_size: number | null;
  last_price: number | null;
  daily_vol: number | null;
  timestamp: string;
}

async function fetchQuotes(): Promise<Quote[]> {
  const res = await fetch(`${API_BASE}/market-data/quotes`);
  if (!res.ok) throw new Error("Network error");
  const data = (await res.json()) as {
    status: number;
    quotes: QuoteDTO[];
  };

  console.log(data);

  return data.quotes.map((q) => ({
    symbol: q.symbol,
    bidPrice: q.bid_price,
    bidSize: q.bid_size,
    askPrice: q.ask_price,
    askSize: q.ask_size,
    lastPrice: q.last_price,
    dailyVol: q.daily_vol,
    timestamp: new Date(q.timestamp),
  }));
}

export function useQuotes() {
  const upsertQuotes = useMarketDataStore((s) => s.upsertQuotes);

  const query = useQuery<Quote[], Error>({
    queryKey: ["quotes"],
    queryFn: fetchQuotes,
    refetchInterval: 1000,
    staleTime: 500,
  });

  useEffect(() => {
    if (query.data) {
      upsertQuotes([...query.data]);
    }
  }, [query.data, upsertQuotes]);

  return query;
}
