import { createFileRoute } from "@tanstack/react-router";
import { useEffect } from "react";

import MarketDataView from "../../components/MarketData/MarketDataView";
import PlaceOrderForm from "../../components/Orders/PlaceOrderForm";
import OrderView from "../../components/Orders/OrderView";
import MiniTicker from "../../components/MarketData/MiniTicker";
import Card from "../../components/UI/Card";
import { usePortfolioDataStore } from "../../stores/portfolioDataStore";
import PortfolioView from "../../components/Portfolio/PortfolioView";

export const Route = createFileRoute("/_authenticated/")({ component: Index });

function Index() {
  const fetchPortfolioData = usePortfolioDataStore(
    (state) => state.fetchPortfolioData,
  );
  const portfolio = usePortfolioDataStore((state) => state.portfolio);

  const fetchPendingOrders = usePortfolioDataStore(
    (state) => state.fetchPendingOrders,
  );

  useEffect(() => {
    (async () => {
      await fetchPortfolioData();
      await fetchPendingOrders();
    })();
  }, [fetchPortfolioData]);

  console.log(portfolio);

  return (
    <div className="min-h-full">
      <MiniTicker />
      <div className="px-6">
        <div className="grid w-full grid-cols-2 grid-rows-[auto_28rem] justify-between gap-8 text-nowrap md:grid-cols-3">
          <Card className="w-full">
            <Card.Title>Cash Available</Card.Title>
            <Card.Total currency="$">{portfolio?.cash}</Card.Total>
          </Card>
          <Card className="h-24 w-full">
            <Card.Title>Total Portfolio Value</Card.Title>
            <Card.Total currency="$">
              {portfolio?.value && Math.round(portfolio.value * 100) / 100}
            </Card.Total>
          </Card>
          <Card className="w-full">
            <Card.Title>Unrealized P/L</Card.Title>
            <Card.Total impact currency="$">
              {portfolio?.totalPnL}
            </Card.Total>
          </Card>
          <MarketDataView />
          <PlaceOrderForm />
          <div>
            <OrderView />
          </div>
        </div>
        <PortfolioView />
      </div>
    </div>
  );
}
