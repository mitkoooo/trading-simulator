import { useMarketDataStore } from "../../stores/marketDataStore";

const MarketDataView = (): React.JSX.Element => {
  const marketData = useMarketDataStore((state) => state.marketData);

  return (
    <div className="border border-divider bg-panel w-[12rem] rounded-md">
      {marketData?.map((stock, index) => (
        <div
          key={stock.symbol}
          className={`flex justify-between w-full p-2 ${index === marketData.length - 1 ? "" : "border-b"} border-divider`}
        >
          <span className="font-semibold">{stock.symbol}</span>
          <span className="font-mono">${stock.price.toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
};

export default MarketDataView;
