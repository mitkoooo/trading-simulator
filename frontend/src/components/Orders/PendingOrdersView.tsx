import { toast, type Toast } from "react-hot-toast";
import { usePortfolioDataStore } from "../../stores/portfolioDataStore";
import { useEffect, useState, type MouseEventHandler } from "react";
import PendingsOrdersRow from "./PendingOrdersRow.tsx";
import { postCancelOrder } from "../../api/trader.ts";
import { LoaderPinwheel } from "lucide-react";

type PendingOrdersViewProps = {
  className?: string;
};

const PendingOrdersView = ({
  className,
}: PendingOrdersViewProps): React.JSX.Element => {
  const pendingOrders = usePortfolioDataStore((s) => s.pendingOrders);
  const fetchPendingOrders = usePortfolioDataStore((s) => s.fetchPendingOrders);

  const handleContainerClick: MouseEventHandler = (e: MouseEvent) => {
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
    <div className={`${className} border-divider relative border-x border-b`}>
      <h1 className="border-divider mx-2 mb-2 border-b py-1 font-semibold tracking-wide uppercase">
        Pending Orders
      </h1>
      <div className="p-1">
        <table className="text-sm">
          <colgroup>
            <col className="w-[10%]" />
            <col className="w-[15%]" />
            <col className="w-[15%]" />
            <col className="w-[18%]" />
            <col className="w-[20%]" />
            <col className="w-[10%]" />
          </colgroup>

          <thead>
            <tr className="border-divider border-b font-semibold tracking-wide text-neutral-400">
              <th scope="col" className="p-1 text-left uppercase">
                Symbol
              </th>
              <th scope="col" className="p-1 text-right uppercase">
                Type
              </th>
              <th scope="col" className="p-1 text-right uppercase">
                Qty
              </th>
              <th scope="col" className="p-1 text-right uppercase">
                Price
              </th>
              <th scope="col" className="p-1 text-right uppercase">
                Status
              </th>
            </tr>
          </thead>
          <tbody onClick={handleContainerClick}>
            {Object.keys(pendingOrders).length !== 0 ? (
              <>
                {Object.values(pendingOrders).map((order, i) => {
                  return (
                    <PendingsOrdersRow
                      className={
                        i == Object.values(pendingOrders).length - 1
                          ? "border-none"
                          : ""
                      }
                      key={order.order_id}
                      order={order}
                    />
                  );
                })}
              </>
            ) : (
              <tr>
                <td colSpan={6} className="text-md p-2 text-center">
                  No orders at the moment.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

type ToastMsgProps = {
  t: Toast;
  orderId: string;
};

const ToastMsg = ({ t, orderId }: ToastMsgProps) => {
  const fetchPendingOrders = usePortfolioDataStore((s) => s.fetchPendingOrders);
  const fetchPortfolioData = usePortfolioDataStore((s) => s.fetchPortfolioData);
  const upsertOrderHistory = usePortfolioDataStore((s) => s.upsertOrderHistory);

  const [toastState, setToastState] = useState<
    "ready" | "loading" | "success" | "error"
  >("ready");

  const onSuccess = async () => {
    setToastState("loading");
    try {
      await postCancelOrder(orderId);
      await Promise.all([
        fetchPendingOrders(),
        fetchPortfolioData(),
        upsertOrderHistory(),
      ]);
      setToastState("success");
      setTimeout(() => toast.dismiss(t.id), 1500); // auto-close on success
    } catch (err) {
      setToastState("error");
    }
  };

  return (
    <div
      className={`${t.visible ? "animate-enter" : "animate-leave"} bg-card text-primary border-divider pointer-events-auto w-full max-w-md flex-col border-2 p-3 shadow-lg`}
    >
      {toastState === "ready" && (
        <>
          <p className="mb-4 text-center">
            Are you sure you want to cancel your order(s)?
          </p>
          <div className="inline-flex w-full justify-between gap-8">
            <button
              className="bg-success text-primary hover:bg-success-hover w-full"
              onClick={onSuccess}
            >
              Yes
            </button>
            <button
              className="bg-error text-primary hover:bg-error-hover w-full"
              onClick={() => toast.dismiss(t.id)}
            >
              No
            </button>
          </div>
        </>
      )}
      {toastState === "loading" && (
        <div className="gap inline-flex h-full w-full items-center justify-center gap-2 select-none">
          <LoaderPinwheel className="text-primary animate-spin" />
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

export default PendingOrdersView;
