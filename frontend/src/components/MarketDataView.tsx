import type { Stock } from "../types/domain";

type MarketDataViewProps = {
  market_data: Stock[] | null;
}; /* use `interface` if exporting so that consumers can extend */

const MarketDataView = ({
  market_data,
}: MarketDataViewProps): React.JSX.Element => {
  return (
    <div>
      {market_data?.map((stock) => (
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
