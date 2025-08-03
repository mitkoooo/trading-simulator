import { useQuery } from "@tanstack/react-query";
import { API_BASE } from "../config/api";
import { useQuotesStore } from "../stores/useQuotesStore";
import { useEffect } from "react";

export interface Quote {
  symbol: string;
  bidPrice: number | null;
  bidSize: number | null;
  askPrice: number | null;
  askSize: number | null;
  lastPrice: number | null;
  timestamp: Date;
}

export interface QuoteDTO {
  symbol: string;
  bid_price: number | null;
  bid_size: number | null;
  ask_price: number | null;
  ask_size: number | null;
  last_price: number | null;
  timestamp: string;
}

async function fetchQuotes(): Promise<Quote[]> {
  const res = await fetch(`${API_BASE}/quotes`);
  if (!res.ok) throw new Error("Network error");
  const data = (await res.json()) as {
    status: number;
    quotes: QuoteDTO[];
  };

  return data.quotes.map((q) => ({
    symbol: q.symbol,
    bidPrice: q.bid_price,
    bidSize: q.bid_size,
    askPrice: q.ask_price,
    askSize: q.ask_size,
    lastPrice: q.last_price,
    timestamp: new Date(q.timestamp),
  }));
}

export function useQuotes() {
  const setQuotes = useQuotesStore((s) => s.setQuotes);

  const query = useQuery<Quote[], Error>({
    queryKey: ["quotes"],
    queryFn: fetchQuotes,
    refetchInterval: 1000,
    staleTime: 500,
  });

  useEffect(() => {
    if (query.data) {
      setQuotes([...query.data]);
    }
  }, [query.data, setQuotes]);

  return query;
}
