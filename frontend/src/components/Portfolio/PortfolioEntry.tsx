import { useShallow } from "zustand/shallow";
import { useMarketDataStore } from "../../stores/marketDataStore";
import type { Position } from "../../types/domain";
import { formatNumber } from "../../utils/utils";
interface PortfolioEntryProps {
  className?: string;
  entry: Position;
} /* use `interface` if exporting so that consumers can extend */

const PortfolioEntry = ({
  className,
  entry,
}: PortfolioEntryProps): React.JSX.Element => {
  const { marketVal } = useMarketDataStore(
    useShallow((s) => ({ marketVal: s.quotes[entry.symbol]?.lastPrice ?? 0 })),
  );

  const pnl = (marketVal - entry.avg_price) * entry.qty;

  const pnlPlaceholder = formatNumber(Math.abs(pnl));

  const pnlCSS = pnl > 0 ? "text-green-400" : pnl < 0 ? "text-error" : "";

  const pnlSign = pnl > 0 ? "+" : pnl < 0 ? "-" : "";

  return (
    <tr className={`border-divider border-b ${className}`}>
      <td className="p-1 text-left">{entry.symbol}</td>
      <td className="p-1 text-right">{entry.qty}</td>
      <td className="p-1 text-right">${formatNumber(entry.avg_price)}</td>
      <td className="p-1 text-right">${formatNumber(marketVal)}</td>
      <td className={`p-1 text-right ${pnlCSS}`}>
        {pnlSign}${pnlPlaceholder}
      </td>
    </tr>
  );
};

export default PortfolioEntry;
