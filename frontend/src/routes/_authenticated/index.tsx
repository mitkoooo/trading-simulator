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
      <div className="flex min-w-[1080px] grow-1 text-nowrap">
        <div className="border-divider flex w-96 shrink-0 flex-col border-x border-b">
          <AccountSummary className="border-divider flex-1 border-b" />
          <OrderHistoryView className="border-divider flex-1 border-b" />
        </div>
        <StockView className="grow-1" />
        <div className="border-divider flex w-96 shrink-0 flex-col border-x border-b">
          <PlaceOrderForm className="border-divider flex-1 border-b" />
          <PendingOrdersView className="border-divider flex-1 border-b" />
          <MarketDataView className="border-divider flex-1 border-b" />
        </div>
      </div>
    </div>
  );
}
