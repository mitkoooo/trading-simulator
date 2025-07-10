import { useEffect, useState } from "react";
import { usePortfolioDataStore } from "../stores/portfolioDataStore";

import { Cross } from "../assets/cross";

import { LoaderPinwheel } from "lucide-react";

import toast, { type Toast } from "react-hot-toast";
import { postCancelOrder } from "../api/trader";

const OrderView = (): React.JSX.Element => {
  const fetchPendingOrders = usePortfolioDataStore(
    (state) => state.fetchPendingOrders,
  );
  const pendingOrders = usePortfolioDataStore((state) => state.pendingOrders);

  const handleContainerClick = (e: EventTarget) => {
    const cross = (e.target as HTMLElement).closest("[data-order-id]");
    if (cross) {
      const orderId = cross.dataset.orderId;
      if (orderId) {
        onCancelOrder(orderId);
      }
    }
  };

  const onCancelOrder = (orderId: string) => {
    toast.custom((t) => <ToastMsg t={t} orderId={orderId} />);
  };

  useEffect(() => {
    (async () => {
      await fetchPendingOrders();
    })();
  }, [fetchPendingOrders]);

  return (
    <div>
      <h1 className="text-xl mb-2">Your pending orders</h1>
      {pendingOrders.length !== 0 ? (
        <div
          className="flex flex-col bg-panel border border-divider rounded-md"
          onClick={handleContainerClick}
        >
          {pendingOrders?.map((o, i) => (
            <div
              className={`w-full justify-between inline-flex p-3 ${i !== pendingOrders.length - 1 ? "" : "border-b"} border-divider items-center`}
              key={o.order_id}
            >
              <div className="inline-flex gap-4">
                <span className="font-semibold ">
                  {o.order_type.toUpperCase()}
                </span>
                <span>{o.symbol}</span>
                <span className="font-mono">${o.limit_price}</span>
                <span>{o.quantity}</span>
              </div>
              <button data-order-id={o.order_id}>
                <Cross className=" text-error hover:text-error-hover min-h-8 min-w-8 h-8 w-8" />
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="flex items-center justify-center text-md">
          No orders at the moment.
        </p>
      )}
    </div>
  );
};

export default OrderView;

type ToastMsgProps = {
  t: Toast;
  orderId: string;
};

const ToastMsg = ({ t, orderId }: ToastMsgProps) => {
  const fetchPendingOrders = usePortfolioDataStore((s) => s.fetchPendingOrders);
  const fetchPortfolioData = usePortfolioDataStore((s) => s.fetchPortfolioData);

  const [toastState, setToastState] = useState<
    "ready" | "loading" | "success" | "error"
  >("ready");

  const onSuccess = async () => {
    setToastState("loading");
    try {
      const res = await postCancelOrder(orderId);
      await Promise.all([fetchPendingOrders(), fetchPortfolioData()]);
      setToastState("success");
      setTimeout(() => toast.dismiss(t.id), 1500); // auto-close on success
    } catch (err) {
      setToastState("error");
    }
  };

  return (
    <div
      className={`${t.visible ? "animate-enter" : "animate-leave"} shadow-lg p-3 max-w-md w-full bg-card text-primary rounded-lg pointer-events-auto flex-col border-2 border-divider`}
    >
      {toastState === "ready" && (
        <>
          <p className="text-center mb-4">
            Are you sure you want to cancel your order(s)?
          </p>
          <div className="w-full inline-flex justify-between gap-8">
            <button
              className="rounded-lg bg-success text-primary w-full bg-panel hover:bg-success-hover"
              onClick={onSuccess}
            >
              Yes
            </button>
            <button
              className="rounded-lg bg-error text-primary w-full hover:bg-error-hover"
              onClick={() => toast.dismiss(t.id)}
            >
              No
            </button>
          </div>
        </>
      )}
      {toastState === "loading" && (
        <div className="inline-flex gap items-center justify-center w-full gap-2 h-full select-none">
          <LoaderPinwheel className="animate-spin text-primary" />
          <p className="font-semibold">Loading...</p>
        </div>
      )}

      {toastState === "success" && (
        <>
          <p>Order has been successfully cancelled.</p>
        </>
      )}
      {toastState === "error" && (
        <>
          <p>Couldn't cancel an order.</p>
        </>
      )}
    </div>
  );
};
