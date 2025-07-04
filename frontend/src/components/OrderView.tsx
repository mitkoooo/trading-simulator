type OrderViewProps = {
  orderVisible: boolean;
}; /* use `interface` if exporting so that consumers can extend */

import { useEffect, useState } from "react";
import type { Order } from "../types/domain";
import { API_BASE } from "../config/api";

const OrderView = ({ orderVisible }: OrderViewProps): React.JSX.Element => {
  const [orders, setOrders] = useState<Order[] | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/me/pending-orders`, {
          method: "GET",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
        });

        if (!res.ok) {
          const errorData = await res.json(); // 👈 this parses the error body
          const errorMessage = errorData.detail || "Unknown error";
          throw Error(errorMessage);
        } else {
          const pendingOrders: Order[] = await res.json();
          console.log(pendingOrders);
          setOrders(pendingOrders);
        }
      } catch (err: unknown) {
        console.error(err);
        throw err;
      }
    })();
  }, [orderVisible]);

  return (
    <div>
      <h3>Your orders</h3>
      {orders?.map((o) => (
        <div className="flex gap-4" key={o.order_id}>
          <span>{o.symbol}</span>
          <span>{o.limit_price}$</span>
          <span>{o.quantity}</span>
        </div>
      ))}
    </div>
  );
};

export default OrderView;
