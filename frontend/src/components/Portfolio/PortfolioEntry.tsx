import type { Position } from "../../types/domain";

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
			className={`bg-panel border-divider flex justify-start gap-8 rounded-md border p-3 ${className} w-sm`}
		>
			<p className="font-semibold">{entry.symbol}</p>
			<p className="font-mono">${entry.avg_price}</p>
			<p>{entry.qty}</p>
		</div>
	);
};

export default PortfolioEntry;
