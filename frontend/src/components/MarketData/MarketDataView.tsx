import { useQuotes } from "../../hooks/useQuotes";
import { useQuotesStore, type Quote } from "../../stores/useQuotesStore";

const MarketDataView = (): React.JSX.Element => {
	useQuotes();
	const quotes: Quote[] = useQuotesStore((s) => s.quotes);
	return (
		<div className="border-divider bg-panel flex h-auto w-[12rem] flex-col rounded-md border">
			{quotes.map((quote, index) => (
				<div
					key={quote.symbol}
					className={`flex h-full w-full items-center justify-between px-2 ${index === quotes.length - 1 ? "" : "border-b"} border-divider`}
				>
					<span className="font-semibold">{quote.symbol}</span>
					<span className="font-mono">${quote?.last?.toFixed(2)}</span>
				</div>
			))}
		</div>
	);
};

export default MarketDataView;
