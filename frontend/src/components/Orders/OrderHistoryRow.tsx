import type React from "react";
import { formatNumber } from "../../utils/utils";
import type { OrderInfo } from "../../types/domain";

interface OrderHistoryRowProps {
  order_info: OrderInfo;
  className: string;
}

const OrderHistoryRow = ({
  className,
  order_info,
}: OrderHistoryRowProps): React.JSX.Element => {
  const price = formatNumber(order_info.avg_fill_price ?? 0);

  return (
    <tr className={`${className} border-b-divider border-b`}>
      <td className="p-1 text-left uppercase">{order_info.symbol}</td>
      <td className="p-1 text-right uppercase">
        {order_info.order_type.toUpperCase()}
      </td>
      <td className="p-1 text-right uppercase">{order_info.fill_qty}</td>
      <td className="p-1 text-right uppercase">
        ${price === "0" ? "N/A" : price}
      </td>
      <td className="p-1 text-right uppercase">{order_info.status}</td>
    </tr>
  );
};

export default OrderHistoryRow;
