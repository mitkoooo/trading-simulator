import { useQuotes } from "../../hooks/useQuotes";
import { useMarketDataStore } from "../../stores/marketDataStore";
import { useStockViewDataStore } from "../../stores/stockViewDataStore";
import type { Quote } from "../../types/domain";

type MarketDataTableProps = {
  className?: string;
};

const MarketDataTable = ({ className }: MarketDataTableProps) => {
  useQuotes();
  const quotes: Record<string, Quote> = useMarketDataStore((s) => s.quotes);
  const setSelectedSymbol = useStockViewDataStore((s) => s.setSelectedSymbol);

  return (
    <div className={`${className ?? ""} px-1 pt-1`}>
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
                className={`${index === Object.keys(quotes).length - 1 ? "" : "border-b"} border-divider`}
              >
                <td className="cursor-pointer p-1 text-left transition-all duration-150 hover:font-semibold">
                  <button onClick={() => setSelectedSymbol(quote.symbol)}>
                    {quote.symbol}
                  </button>
                </td>
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
  );
};

export default MarketDataTable;
