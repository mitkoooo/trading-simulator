import { useEffect } from "react";
import { usePortfolioDataStore } from "../../stores/portfolioDataStore";
import { formatNumber } from "../../utils/utils";
import PortfolioView from "./PortfolioView";
import { useMarketDataStore } from "../../stores/marketDataStore";
import type { Quote } from "../../types/domain";

type AccountSummaryProps = {
  className?: string;
};

const AccountSummary = ({
  className,
}: AccountSummaryProps): React.JSX.Element => {
  const fetchPortfolioData = usePortfolioDataStore(
    (state) => state.fetchPortfolioData,
  );
  const portfolio = usePortfolioDataStore((state) => state.portfolio);
  const positions = portfolio.positions;
  const quotes: Record<string, Quote> = useMarketDataStore((s) => s.quotes);

  let unrealizedPnL = 0;
  for (const p of positions) {
    const price: number = quotes[p.symbol].lastPrice ?? 0;
    unrealizedPnL += (price - p.avg_price) * p.qty;
  }

  useEffect(() => {
    (async () => {
      await fetchPortfolioData();
    })();
  }, [fetchPortfolioData]);

  const pnlPlaceholder = (pnl: number | null): string =>
    formatNumber(Math.abs(pnl ?? 0));

  const pnlCSS = (pnl: number | null): string =>
    (pnl ?? 0) > 0 ? "text-green-400" : (pnl ?? 0) < 0 ? "text-error" : "";

  const pnlSign = (pnl: number | null): string =>
    (pnl ?? 0) > 0 ? "+" : (pnl ?? 0) < 0 ? "-" : "";

  return (
    <div
      className={`${className} border-divider flex flex-col border-x border-b`}
    >
      <h1 className="border-divider mx-1 border-b py-1 font-semibold tracking-wide">
        ACCOUNT SUMMARY
      </h1>
      <div className="border-divider flex flex-col border-b pb-2 text-sm">
        <div className="mx-1 flex flex-row items-center justify-between py-1">
          <span className="tracking-wider text-neutral-400 uppercase">
            cash
          </span>
          <span className="font-semibold">
            ${formatNumber(portfolio?.cash ?? 0)}
          </span>
        </div>
        <div className="mx-1 flex flex-row items-center justify-between py-1">
          <span className="tracking-wider text-neutral-400 uppercase">
            portfolio value
          </span>
          <span className="font-semibold">
            ${formatNumber(portfolio?.value ?? 0)}
          </span>
        </div>
        <div className="mx-1 flex flex-row items-center justify-between py-1">
          <span className="tracking-wider text-neutral-400 uppercase">
            unrealized p&l
          </span>
          <span className={`font-semibold ${pnlCSS(unrealizedPnL)}`}>
            {pnlSign(unrealizedPnL)}${pnlPlaceholder(unrealizedPnL)}
          </span>
        </div>
        <div className="mx-1 flex flex-row items-center justify-between py-1">
          <span className="tracking-wider text-neutral-400 uppercase">p&l</span>
          <span className={`font-semibold ${pnlCSS(portfolio?.realizedPnL)}`}>
            {pnlSign(portfolio?.realizedPnL)}$
            {pnlPlaceholder(portfolio?.realizedPnL)}
          </span>
        </div>
      </div>

      <PortfolioView className="mt-2 min-h-0 flex-1" />
    </div>
  );
};

export default AccountSummary;
