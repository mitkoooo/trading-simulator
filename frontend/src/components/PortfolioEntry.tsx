import type { Position } from "../types/domain";

interface PortfolioEntryProps {
  className: string;
  entry: Position;
} /* use `interface` if exporting so that consumers can extend */

const PortfolioEntry = ({
  className,
  entry,
}: PortfolioEntryProps): React.JSX.Element => (
  <div
    className={`flex text-3xl gap-8 text-yellow-600 border p-2 w-xl justify-start ${className}`}
  >
    <p>{entry.ticket}</p>
    <p>{entry.qty}</p>
    <p>{entry.avg_price}$</p>
  </div>
);

export default PortfolioEntry;
