import type { Position } from "../types/domain";

interface PortfolioEntryProps {
  className?: string;
  entry: Position;
} /* use `interface` if exporting so that consumers can extend */

const PortfolioEntry = ({
  className,
  entry,
}: PortfolioEntryProps): React.JSX.Element => {
  console.log(entry);

  return (
    <div
      className={`bg-panel border-divider rounded-md flex  gap-8  border p-3  justify-start ${className} w-sm`}
    >
      <p className="font-semibold">{entry.symbol}</p>
      <p className="font-mono">${entry.avg_price}</p>
      <p>{entry.qty}</p>
    </div>
  );
};

export default PortfolioEntry;
