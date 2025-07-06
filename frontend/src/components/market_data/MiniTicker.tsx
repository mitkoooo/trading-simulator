import type { Stock } from "../../types/domain";

interface MiniTickerProps {
  className?: string;
  marketData: Stock[] | null;
}

const MiniTicker = ({
  className = "",
  marketData,
}: MiniTickerProps): React.JSX.Element => {
  const renderTickers = (keySuffix: string = "") => {
    return marketData?.map((stock, index) => {
      const percentageChange =
        stock?.history.length > 1
          ? (stock.price - stock.history[stock.history.length - 2]) /
            stock.history[stock.history.length - 2]
          : 0.0;

      let changeColor = "text-disabled";
      if (percentageChange > 0) changeColor = "text-success";
      else if (percentageChange < 0) changeColor = "text-error";

      const formattedChange = `${percentageChange > 0 ? "+" : ""}${percentageChange.toFixed(3)}%`;

      return (
        <div
          key={`${stock.symbol}-${keySuffix}`}
          className="absolute top-[25%] h-full flex flex-col items-start px-4 animate-ticker-item"
          style={{ animationDelay: `${index * 4}s` }}
        >
          <div className="flex items-baseline gap-1">
            <span className="font-semibold">{stock.symbol}</span>
            <span className="font-mono">${stock.price.toFixed(1)}</span>
          </div>

          <div className={`text-xs ${changeColor}`}>{formattedChange}</div>
        </div>
      );
    });
  };

  return (
    <div className={`${className} overflow-hidden h-14  relative text-primary`}>
      <div className=" w-full h-full">
        {renderTickers()}
        {renderTickers("-dup")}
      </div>
    </div>
  );
};

export default MiniTicker;
