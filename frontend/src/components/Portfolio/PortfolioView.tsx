import { usePortfolioDataStore } from "../../stores/portfolioDataStore";
import PortfolioEntry from "./PortfolioEntry";

const PortfolioView = (): React.JSX.Element => {
  const portfolio = usePortfolioDataStore((state) => state.portfolio);

  console.log(portfolio);

  return (
    <div className="bg-canvas mt-10 flex flex-col items-start justify-between">
      <h1 className="mb-1 text-xl">Your holdings</h1>{" "}
      {portfolio &&
        portfolio.positions.map((position) => (
          <PortfolioEntry
            entry={position}
            key={position.symbol}
          ></PortfolioEntry>
        ))}
    </div>
  );
};

export default PortfolioView;
