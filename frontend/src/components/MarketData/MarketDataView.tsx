import { useQuotes } from "../../hooks/useQuotes";
import { useMarketDataStore } from "../../stores/marketDataStore";
import type { Quote } from "../../types/domain";

type MarketDataViewProps = {
  className?: string;
};

const MarketDataView = ({
  className,
}: MarketDataViewProps): React.JSX.Element => {
  useQuotes();
  const quotes: Record<string, Quote> = useMarketDataStore((s) => s.quotes);

  return (
    <div className={`${className} border-divider border-x border-b`}>
      <h1 className="border-divider mx-1 mb-1 border-b py-1 font-semibold tracking-wide uppercase">
        Market Watch
      </h1>
      <div className="p-1">
        <table className="text-sm">
          <colgroup>
            <col className="w-[5%]" />
            <col className="w-[15%]" />
            <col className="w-[15%]" />
            <col className="w-[15%]" />
            <col className="w-[10%]" />
          </colgroup>
          <thead>
            <tr className="border-divider border-b font-semibold tracking-wide text-neutral-400">
              <th scope="col" className="p-1 text-left uppercase">
                Symbol
              </th>
              <th scope="col" className="p-1 text-right uppercase">
                Bid
              </th>
              <th scope="col" className="p-1 text-right uppercase">
                Ask
              </th>
              <th scope="col" className="p-1 text-right uppercase">
                Last
              </th>
              <th scope="col" className="p-1 text-right uppercase">
                Volume
              </th>
            </tr>
          </thead>
          <tbody>
            {Object.values(quotes).map((quote, index) => {
              return (
                <tr
                  key={quote.symbol}
                  className={`${index === quotes.length - 1 ? "" : "border-b"} border-divider`}
                >
                  <td className="p-1 text-left">{quote.symbol}</td>
                  <td className="p-1 text-right">
                    ${quote?.bidPrice?.toFixed(2)}
                  </td>
                  <td className="p-1 text-right">
                    ${quote?.askPrice?.toFixed(2)}
                  </td>
                  <td className="p-1 text-right">
                    ${quote?.lastPrice?.toFixed(2)}
                  </td>
                  <td className="p-1 text-right uppercase">
                    {quote?.dailyVol ?? "N/A"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MarketDataView;
