import type React from "react";
import type { Order } from "../../types/domain";
import { Cross } from "../../assets/cross";
import { formatNumber } from "../../utils/utils";

interface OrderHistoryRowProps {
  order: Order;
  className: string;
}

const PendingOrdersRow = ({
  className,
  order,
}: OrderHistoryRowProps): React.JSX.Element => {
  const price = formatNumber(order.limit_price ?? 0);

  return (
    <tr className={`${className} border-b-divider border-b`}>
      <td className="p-1 text-left uppercase">{order.symbol}</td>
      <td className="p-1 text-right uppercase">
        {order.order_type.toUpperCase()}
      </td>
      <td className="p-1 text-right uppercase">{order.quantity}</td>
      <td className="p-1 text-right uppercase">
        ${price === "0" ? "N/A" : price}
      </td>
      <td className="p-1 text-right uppercase">{order.status}</td>
      <td className="p-1 text-right uppercase">
        <button data-order-id={order.order_id}>
          <Cross className="text-error hover:text-error-hover min-h-7 min-w-7" />
        </button>
      </td>
    </tr>
  );
};

export default PendingOrdersRow;
