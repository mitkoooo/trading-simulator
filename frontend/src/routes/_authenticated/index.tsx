import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState, type MouseEventHandler } from "react";
import PortfolioEntry from "../../components/PortfolioEntry";
import type { Portfolio, Stock } from "../../types/domain";
import { getPortfolio } from "../../api/portfolio";
import MarketDataView from "../../components/market_data/MarketDataView";
import { getMarketData, nextTick } from "../../api/marketdata";
import PlaceOrderForm from "../../components/PlaceOrderForm";
import OrderView from "../../components/OrderView";
import { getMatchOrders } from "../../api/exchange";
import MiniTicker from "../../components/market_data/MiniTicker";
import Card from "../../components/Card";

export const Route = createFileRoute("/_authenticated/")({ component: Index });

function Index() {
  const [portfolio, setPortfolio] = useState<null | Portfolio>(null);
  const [marketData, setMarketData] = useState<null | Stock[]>(null);

  const [orderVisible, setOrderVisible] = useState<boolean>(false);
  const [orderType, setOrderType] = useState<string | null>(null);

  const onClick: MouseEventHandler<HTMLButtonElement> = (e) => {
    const order = e.target as HTMLButtonElement;

    setOrderVisible(true);
    setOrderType(order.textContent);
  };

  useEffect(() => {
    (async () => {
      const newPortfolio = await getPortfolio();
      setPortfolio(newPortfolio);
      const newMarketData = await getMarketData();
      setMarketData(newMarketData);
    })();
  }, [orderVisible]);

  const onNextPrice = async () => {
    const newMarketData = await nextTick();
    setMarketData(newMarketData);
    const newPortfolio = await getPortfolio();
    setPortfolio(newPortfolio);
  };

  const onMatchOrders = async () => {
    await getMatchOrders();

    const newPortfolio = await getPortfolio();
    setPortfolio(newPortfolio);
  };

  return (
    <div>
      <MiniTicker marketData={marketData} />
      <div className="px-3">
        <div className=" inline-flex w-full items-center justify-between mb-4 h-32 text-nowrap gap-12">
          <Card className="w-full">
            <Card.Title>Cash Available</Card.Title>
            <Card.Total currency="$">{portfolio?.cash}</Card.Total>
          </Card>
          <Card className="w-full">
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
        </div>
        <div className="flex items-center justify-between bg-canvas">
          {portfolio &&
            portfolio.positions.map((position) => (
              <PortfolioEntry
                className="mt-10"
                entry={position}
                key={position.ticket}
              ></PortfolioEntry>
            ))}
          <MarketDataView marketData={marketData} />
          <OrderView orderVisible={orderVisible} />
          <div>
            <button
              className="py-1 h-8 px-4 bg-rose-800 border border-rose-950 duration-150 rounded-md hover:bg-rose-900 hover:border-rose-900"
              onClick={onMatchOrders}
            >
              Match orders
            </button>
            <button
              className="py-1 h-8 px-4 bg-blue-800 border border-blue-950 duration-150 rounded-md hover:bg-blue-900 hover:border-blue-900"
              onClick={onNextPrice}
            >
              Next price
            </button>
            <div className="flex gap-4">
              <button
                className="py-1 h-8 px-4 border border-green-800 bg-green-600 hover:bg-green-700 duration-150 rounded-md hover:border-green-700"
                onClick={onClick}
              >
                Buy
              </button>

              <button
                className="px-4 h-8 border border-red-800 bg-red-600 hover:bg-red-700 hover:border-red-700 duration-150 rounded-md"
                onClick={onClick}
              >
                Sell
              </button>
            </div>
          </div>
        </div>
        {orderVisible && (
          <PlaceOrderForm
            onOrderVisible={setOrderVisible}
            orderType={orderType}
          />
        )}
      </div>
    </div>
  );
}
