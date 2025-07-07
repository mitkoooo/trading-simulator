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
    (state) => state.fetchPortfolioData
  );
  const portfolio = usePortfolioDataStore((state) => state.portfolio);

  const fetchNextMarketData = useMarketDataStore(
    (state) => state.fetchNextMarketData
  );

  useEffect(() => {
    (async () => {
      fetchNextMarketData();
      fetchPortfolioData();
    })();
  }, [fetchNextMarketData, fetchPortfolioData]);

  const onNextPrice = async () => {
    fetchNextMarketData();
    fetchPortfolioData();
  };

  const onMatchOrders = async () => {
    await getMatchOrders();
    fetchPortfolioData();
  };

  return (
    <div className="min-h-full">
      <MiniTicker />
      <div className="px-6  grid grid-rows-[auto_auto]">
        <div className="grid grid-cols-2 md:grid-cols-3 w-full justify-between text-nowrap gap-8 ">
          <Card className="w-full ">
            <Card.Title>Cash Available</Card.Title>
            <Card.Total currency="$">{portfolio?.cash}</Card.Total>
          </Card>
          <Card className="w-full h-24">
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
            <div className="inline-flex mt-3 w-full justify-between gap-4">
              <button
                className="py-1 h-8 px-4 bg-success border border-divider duration-150 rounded-md hover:bg-success-hover w-full focus:outline-1 focus:outline-accent"
                onClick={onMatchOrders}
              >
                Match orders
              </button>
              <button
                className="py-1 h-8 px-4 bg-info border border-divider duration-150 rounded-md hover:bg-info-hover w-full focus:outline-1 focus:outline-accent"
                onClick={onNextPrice}
              >
                Next price
              </button>
            </div>
          </div>
        </div>
        <div className="flex flex-col items-start justify-between bg-canvas mt-10">
          <h1 className="text-xl mb-1">Your holdings</h1>
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
