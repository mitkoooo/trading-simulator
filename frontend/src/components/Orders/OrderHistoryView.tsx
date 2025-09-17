import { useEffect, useState } from "react";
import { usePortfolioDataStore } from "../../stores/portfolioDataStore";
import OrderHistoryRow from "./OrderHistoryRow";
import type { OrderInfo } from "../../types/domain";

type OrderHistoryViewProps = {
  className?: string;
};

const OrderHistoryView = ({
  className,
}: OrderHistoryViewProps): React.JSX.Element => {
  const upsertOrderHistory = usePortfolioDataStore(
    (state) => state.upsertOrderHistory,
  );
  const orderHistory: Record<string, OrderInfo> = usePortfolioDataStore(
    (state) => state.orderHistory,
  );

  const maxLines = 10;
  const maxPageNumber = Math.floor(
    Object.values(orderHistory).length / maxLines,
  );

  const [pageNumber, setPageNumber] = useState<number>(0);

  const handleClickPrev = () => {
    if (pageNumber == 0) return;

    setPageNumber((prev) => --prev);
  };

  const handleClickNext = () => {
    if (pageNumber == maxPageNumber) return;

    setPageNumber((prev) => ++prev);
  };

  useEffect(() => {
    (async () => {
      await upsertOrderHistory();
    })();
  }, [upsertOrderHistory]);

  return (
    <div className={`${className} border-divider relative border-x border-b`}>
      <h1 className="border-divider mx-2 mb-2 border-b py-1 font-semibold tracking-wide uppercase">
        Order History
      </h1>
      <div className="block min-h-0 flex-1 overflow-y-auto p-1">
        <table className="text-sm">
          <colgroup>
            <col className="w-[10%]" />
            <col className="w-[15%]" />
            <col className="w-[15%]" />
            <col className="w-[18%]" />
            <col className="w-[20%]" />
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
          <tbody>
            {Object.keys(orderHistory).length !== 0 ? (
              <>
                {Object.values(orderHistory)
                  ?.slice(pageNumber * maxLines, (pageNumber + 1) * maxLines)
                  .map((order_info, i) => {
                    return (
                      <OrderHistoryRow
                        className={`${
                          i === maxLines - 1 ||
                          i + maxLines * pageNumber ==
                            Object.values(orderHistory).length - 1
                            ? "border-none"
                            : ""
                        }`}
                        key={order_info.order_id}
                        order_info={order_info}
                      />
                    );
                  })}
              </>
            ) : (
              <tr>
                <td colSpan={5} className="text-md p-2 text-center">
                  No orders history.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="absolute right-0 bottom-2 left-0 flex items-center justify-center gap-4">
        <button
          className="border-divider border p-1 tracking-wider uppercase"
          onClick={handleClickPrev}
        >
          Prev
        </button>{" "}
        <span>{pageNumber + 1}</span>
        <button
          className="border-divider border p-1 tracking-wider uppercase"
          onClick={handleClickNext}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default OrderHistoryView;
