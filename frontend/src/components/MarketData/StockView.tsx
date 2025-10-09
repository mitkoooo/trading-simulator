import { useState } from "react";

type StockViewProps = {
  className?: string;
}; /* use `interface` if exporting so that consumers can extend */

const StockView = ({ className }: StockViewProps): React.JSX.Element => {
  const [stock, setStock] = useState<string | null>(null);

  return (
    <div className={className}>Stock view - {stock ?? "None selected"}</div>
  );
};
export default StockView;
