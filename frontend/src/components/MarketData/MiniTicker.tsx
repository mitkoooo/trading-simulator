import { useMarketDataStore } from "../../stores/marketDataStore";

interface MiniTickerProps {
	className?: string;
}

const MiniTicker = ({ className = "" }: MiniTickerProps): React.JSX.Element => {
	const marketData = useMarketDataStore((state) => state.marketData);

	const stocks = marketData ? Array.from(marketData.values()) : [];

	const renderTickers = (keySuffix: string = "") => {
		return stocks.map((stock, index) => {
			const percentageChange =
				stock?.history.length > 1
					? ((stock.price - stock.history[stock.history.length - 2]) /
						stock.history[stock.history.length - 2]) *
					100
					: 0.0;

			let changeColor = "text-disabled";
			if (percentageChange > 0) changeColor = "text-success";
			else if (percentageChange < 0) changeColor = "text-error";

			const formattedChange = `${percentageChange > 0 ? "+" : ""}${percentageChange.toFixed(2)}%`;

			return (
				<div
					key={`${stock.symbol}-${keySuffix}`}
					className="animate-ticker-item absolute top-[15%] flex h-full flex-col items-start px-4"
					style={{ animationDelay: `${index * 4}s` }}
				>
					<div className="flex items-baseline gap-1">
						<span className="font-semibold">{stock.symbol}</span>
						<span className="font-mono">${stock.price.toFixed(2)}</span>
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
