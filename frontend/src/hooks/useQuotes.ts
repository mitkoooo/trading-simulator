import { useQuery } from "@tanstack/react-query";
import { API_BASE } from "../config/api";
import { useQuotesStore } from "../stores/useQuotesStore";
import { useEffect } from "react";

export interface Quote {
	symbol: string;
	bid_price: number | null;
	bid_size: number | null;
	ask_price: number | null;
	ask_size: number | null;
	last: number | null;
	timestamp: Date;
}

async function fetchQuotes(): Promise<Quote[]> {
	const res = await fetch(`${API_BASE}/quotes`);
	if (!res.ok) throw new Error("Network error");
	const data = (await res.json()) as {
		symbol: string;
		bid_price: number | null;
		bid_size: number | null;
		ask_price: number | null;
		ask_size: number | null;
		last: number | null;
		timestamp: string;
	}[];
	return data.map((q) => ({
		...q,
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
		console.log("Syncing", query.data);
		if (query.data) {
			setQuotes([...query.data]);
		}
	}, [query.data, setQuotes]);

	return query;
}
