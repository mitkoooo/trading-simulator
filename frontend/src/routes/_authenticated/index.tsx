import { createFileRoute } from "@tanstack/react-router";
import { useEffect } from "react";

import { getMatchOrders } from "../../api/exchange";

import { useMarketDataStore } from "../../stores/marketDataStore";

import PortfolioEntry from "../../components/PortfolioEntry";
import MarketDataView from "../../components/market_data/MarketDataView";
import PlaceOrderForm from "../../components/PlaceOrderForm";
import OrderView from "../../components/OrderView";
import MiniTicker from "../../components/market_data/MiniTicker";
import Card from "../../components/Card";
import { usePortfolioDataStore } from "../../stores/portfolioDataStore";

export const Route = createFileRoute("/_authenticated/")({ component: Index });

function Index() {
  const fetchPortfolioData = usePortfolioDataStore(
    (state) => state.fetchPortfolioData,
  );
  const portfolio = usePortfolioDataStore((state) => state.portfolio);

  const fetchMarketData = useMarketDataStore((state) => state.fetchMarketData);

  const fetchNextMarketData = useMarketDataStore(
    (state) => state.fetchNextMarketData,
  );

  const fetchPendingOrders = usePortfolioDataStore(
    (state) => state.fetchPendingOrders,
  );

  useEffect(() => {
    (async () => {
      await fetchMarketData();
      await fetchPortfolioData();
    })();
  }, [fetchMarketData, fetchPortfolioData]);

  const onNextPrice = async () => {
    await fetchNextMarketData();
    await fetchPortfolioData();
  };

  const onMatchOrders = async () => {
    await getMatchOrders();
    await fetchPendingOrders();
    await fetchPortfolioData();
  };

  return (
    <div className="min-h-full">
      <MiniTicker />
      <div className="grid grid-rows-[auto_auto] px-6">
        <div className="grid w-full grid-cols-2 justify-between gap-8 text-nowrap md:grid-cols-3">
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
            <div className="mt-3 inline-flex w-full justify-between gap-4">
              <button
                className="bg-success border-divider hover:bg-success-hover focus:outline-accent h-8 w-full rounded-md border px-4 py-1 duration-150 focus:outline-1"
                onClick={onMatchOrders}
              >
                Match orders
              </button>
              <button
                className="bg-info border-divider hover:bg-info-hover focus:outline-accent h-8 w-full rounded-md border px-4 py-1 duration-150 focus:outline-1"
                onClick={onNextPrice}
              >
                Next price
              </button>
            </div>
          </div>
        </div>
        <div className="bg-canvas mt-10 flex flex-col items-start justify-between">
          <h1 className="mb-1 text-xl">Your holdings</h1>
          {portfolio &&
            portfolio.positions.map((position) => (
              <PortfolioEntry
                entry={position}
                key={position.symbol}
              ></PortfolioEntry>
            ))}
        </div>
      </div>
    </div>
  );
}
