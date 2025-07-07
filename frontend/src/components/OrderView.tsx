import { useEffect } from "react";
import { usePortfolioDataStore } from "../stores/portfolioDataStore";

const OrderView = (): React.JSX.Element => {
  const fetchPendingOrders = usePortfolioDataStore(
    (state) => state.fetchPendingOrders
  );
  const pendingOrders = usePortfolioDataStore((state) => state.pendingOrders);

  useEffect(() => {
    (async () => {
      fetchPendingOrders();
    })();
  }, [fetchPendingOrders]);

  return (
    <div>
      <h1 className="text-xl mb-2">Your pending orders</h1>
      {pendingOrders.length !== 0 ? (
        <div className="bg-panel border border-divider rounded-md">
          {pendingOrders?.map((o, i) => (
            <div
              className={`flex gap-4 p-3 ${i !== pendingOrders.length - 1 ? "" : "border-b"} border-divider`}
              key={o.order_id}
            >
              <span className="font-semibold ">
                {o.order_type.toUpperCase()}
              </span>
              <span>{o.symbol}</span>
              <span className="font-mono">${o.limit_price}</span>
              <span>{o.quantity}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="flex items-center justify-center text-xl">
          No orders at the moment.
        </p>
      )}
    </div>
  );
};

export default OrderView;
