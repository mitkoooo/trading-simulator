import { useEffect } from "react";
import {
  useMarketDataStore,
  type DailySummary,
} from "../../stores/marketDataStore";
import { getDailySummaries } from "../../api/marketData";
import type { Quote } from "../../types/domain";
import { useShallow } from "zustand/shallow";

interface MiniTickerProps {
  className?: string;
}

const MiniTicker = ({ className = "" }: MiniTickerProps): React.JSX.Element => {
  const quotes: Record<string, Quote> = useMarketDataStore((s) => s.quotes);
  const dailySummaries: Record<string, DailySummary> = useMarketDataStore(
    (s) => s.dailySummaries,
  );
  const upsertSummaries = useMarketDataStore((s) => s.upsertSummaries);

  useEffect(() => {
    (async () => {
      const data = await getDailySummaries();
      upsertSummaries(data.summaries);
    })();
  }, []);

  const renderTickers = (keySuffix: string = "") => {
    return Object.keys(quotes).map((symbol, index) => {
      let percentageChange = 0;

      const lastPrice = quotes[symbol]?.lastPrice ?? 0;

      const previousClose = dailySummaries[symbol]?.previous_close ?? 0;

      if (previousClose && lastPrice) {
        percentageChange = ((lastPrice - previousClose) / previousClose) * 100;
      }

      percentageChange = Math.round(percentageChange * 100) / 100;

      let changeColor = "text-disabled";
      if (percentageChange > 0) changeColor = "text-green-400";
      else if (percentageChange < 0) changeColor = "text-error";

      const formattedChange = `${percentageChange > 0 ? "+" : ""}${percentageChange.toFixed(2)}%`;

      return (
        <div
          key={`${symbol}-${keySuffix}`}
          className="animate-ticker-item absolute top-[10%] flex h-full flex-col items-start px-4"
          style={{ animationDelay: `${index * 4}s` }}
        >
          <div className="flex items-baseline gap-1">
            <span className="font-semibold">{symbol}</span>
            <span className="font-thin text-neutral-400">
              ${lastPrice?.toFixed(2)}
            </span>
            <div className={`font-semibold ${changeColor}`}>
              {formattedChange}
            </div>
          </div>
        </div>
      );
    });
  };

  return (
    <div
      className={`${className} text-primary bg-panel border-divider relative h-6 items-center overflow-hidden border-b text-sm`}
    >
      <div className="h-full w-full">
        {renderTickers()}
        {renderTickers("-dup")}
      </div>
    </div>
  );
};

export default MiniTicker;
