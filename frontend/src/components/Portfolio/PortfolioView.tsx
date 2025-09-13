import { usePortfolioDataStore } from "../../stores/portfolioDataStore";
import PortfolioEntry from "./PortfolioEntry";

interface PortfolioViewProps {
  className?: string;
}

const PortfolioView = ({
  className,
}: PortfolioViewProps): React.JSX.Element => {
  const portfolio = usePortfolioDataStore((state) => state.portfolio);

  return (
    <div className={`bg-canvas h-full ${className}`}>
      <h1 className="border-divider mx-1 border-b py-1 font-semibold tracking-wide">
        PORTFOLIO HOLDINGS
      </h1>
      <table className="text-sm">
        <colgroup>
          <col className="w-[14%]" />
          <col className="w-[10%]" />
          <col className="w-[18%]" />
          <col className="w-[18%]" />
          <col className="w-[18%]" />
        </colgroup>

        <thead>
          <tr className="border-divider border-b font-semibold tracking-wide text-neutral-400">
            <th scope="col" className="p-1 text-left">
              SYMBOL
            </th>
            <th scope="col" className="p-1 text-right">
              QTY
            </th>
            <th scope="col" className="p-1 text-right">
              AVG COST
            </th>
            <th scope="col" className="p-1 text-right">
              MARKET VAL
            </th>
            <th scope="col" className="p-1 text-right">
              P&L
            </th>
          </tr>
        </thead>
        <tbody>
          {portfolio &&
            portfolio.positions.map((position, i) => {
              return (
                <PortfolioEntry
                  entry={position}
                  key={position.symbol}
                  className={`${i === portfolio.positions.length - 1 ? "border-none" : ""}`}
                />
              );
            })}
        </tbody>
      </table>
    </div>
  );
};

export default PortfolioView;
