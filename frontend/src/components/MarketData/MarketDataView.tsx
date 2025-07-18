import { useMarketDataStore } from "../../stores/marketDataStore";

const MarketDataView = (): React.JSX.Element => {
	const marketData = useMarketDataStore((state) => state.marketData);

	const stocks = marketData ? Array.from(marketData.values()) : [];

	return (
		<div className="border-divider bg-panel flex h-auto w-[12rem] flex-col rounded-md border">
			{stocks.map((stock, index) => (
				<div
					key={stock.symbol}
					className={`flex h-full w-full items-center justify-between px-2 ${index === stocks.length - 1 ? "" : "border-b"} border-divider`}
				>
					<span className="font-semibold">{stock.symbol}</span>
					<span className="font-mono">${stock.price.toFixed(2)}</span>
				</div>
			))}
		</div>
	);
};

export default MarketDataView;
