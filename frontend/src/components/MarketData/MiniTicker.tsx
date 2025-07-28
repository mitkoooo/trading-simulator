import { useQuotesStore, type Quote } from "../../stores/useQuotesStore";

interface MiniTickerProps {
	className?: string;
}

const MiniTicker = ({ className = "" }: MiniTickerProps): React.JSX.Element => {
	const quotes: Quote[] = useQuotesStore((s) => s.quotes);

	const renderTickers = (keySuffix: string = "") => {
		return quotes.map((quote, index) => {
			const percentageChange = 1;
			let changeColor = "text-disabled";
			if (percentageChange > 0) changeColor = "text-success";
			else if (percentageChange < 0) changeColor = "text-error";

			const formattedChange = `${percentageChange > 0 ? "+" : ""}${percentageChange.toFixed(2)}%`;

			return (
				<div
					key={`${quote.symbol}-${keySuffix}`}
					className="animate-ticker-item absolute top-[15%] flex h-full flex-col items-start px-4"
					style={{ animationDelay: `${index * 4}s` }}
				>
					<div className="flex items-baseline gap-1">
						<span className="font-semibold">{quote?.symbol}</span>
						<span className="font-mono">${quote?.last?.toFixed(2)}</span>
					</div>

					<div className={`text-xs ${changeColor}`}>{formattedChange}</div>
				</div>
			);
		});
	};

	return (
		<div className={`${className} text-primary relative h-14 overflow-hidden`}>
			<div className="h-full w-full">
				{renderTickers()}
				{renderTickers("-dup")}
			</div>
		</div>
	);
};

export default MiniTicker;
