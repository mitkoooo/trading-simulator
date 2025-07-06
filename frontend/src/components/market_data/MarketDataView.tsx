import type { Stock } from "../../types/domain";

type MarketDataViewProps = {
  marketData: Stock[] | null;
}; /* use `interface` if exporting so that consumers can extend */

const MarketDataView = ({
  marketData,
}: MarketDataViewProps): React.JSX.Element => {
  return (
    <div>
      {marketData?.map((stock) => (
        <div
          key={stock.symbol}
          className="border flex justify-between w-40 p-2"
        >
          <span className="font-semibold">{stock.symbol}</span>
          <span className="font-mono">
            {Math.round(stock.price * 10) / 10}$
          </span>
        </div>
      ))}
    </div>
  );
};

export default MarketDataView;
