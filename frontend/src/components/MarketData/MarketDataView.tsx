import MarketDataTable from "./MarketDataTable";
import StockView from "./StockView";

type MarketDataViewProps = {
  className?: string;
};

const MarketDataView = ({
  className,
}: MarketDataViewProps): React.JSX.Element => {
  return (
    <div className={`${className}`}>
      <h1 className="border-divider mx-1 mb-1 border-b py-1 font-semibold tracking-wide uppercase">
        Market Watch
      </h1>
      <div className="flex flex-col">
        <MarketDataTable className="flex-1" />
      </div>
    </div>
  );
};

export default MarketDataView;
