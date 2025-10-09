import { createFileRoute } from "@tanstack/react-router";

import MarketDataView from "../../components/MarketData/MarketDataView";
import PlaceOrderForm from "../../components/Orders/PlaceOrderForm";
import OrderHistoryView from "../../components/Orders/OrderHistoryView";
import MiniTicker from "../../components/MarketData/MiniTicker";
import AccountSummary from "../../components/Portfolio/AccountSummary";
import PendingOrdersView from "../../components/Orders/PendingOrdersView";
import StockView from "../../components/MarketData/StockView";

export const Route = createFileRoute("/_authenticated/")({ component: Index });

function Index() {
  return (
    <div className="flex flex-1 flex-col">
      <MiniTicker />
      <div className="grid min-w-[1080px] flex-1 grid-cols-3 text-nowrap">
        <div className="flex flex-col">
          <MarketDataView className="flex-1" />
          <StockView className="flex-1" />
        </div>
        <div className="flex flex-col">
          <PlaceOrderForm className="flex-1" />
          <PendingOrdersView className="flex-1" />
        </div>
        <div className="flex flex-col">
          <AccountSummary className="flex-1" />
          <OrderHistoryView className="flex-1" />
        </div>
      </div>
    </div>
  );
}
