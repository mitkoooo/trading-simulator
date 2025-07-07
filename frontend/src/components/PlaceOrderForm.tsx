import { useForm, type SubmitHandler } from "react-hook-form";

import { API_BASE } from "../config/api";
import { useState, type MouseEventHandler } from "react";
import { usePortfolioDataStore } from "../stores/portfolioDataStore";

interface PlaceOrderFormData {
  symbol: string;
  quantity: number;
  price: number;
}

const InputClass =
  "px-2 py-1 bg-card border-2 rounded-md text-primary border-divider w-full focus:bg-card focus:outline-1 focus:outline-accent";

const PlaceOrderForm = (): React.JSX.Element => {
  const {
    register,
    reset,
    handleSubmit,
    formState: { errors },
  } = useForm<PlaceOrderFormData>();

  const fetchPortfolioData = usePortfolioDataStore(
    (state) => state.fetchPortfolioData
  );
  const fetchPendingOrders = usePortfolioDataStore(
    (state) => state.fetchPendingOrders
  );

  const [error, setError] = useState<string | null>(null);
  const [orderType, setOrderType] = useState<string | null>(null);

  const onClick: MouseEventHandler<HTMLButtonElement> = (e) => {
    const order = e.target as HTMLButtonElement;
    setOrderType(order.textContent);
  };

  const handlePlaceOrderSubmit: SubmitHandler<PlaceOrderFormData> = async (
    data: PlaceOrderFormData
  ) => {
    const res = await fetch(`${API_BASE}/order`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ order_type: orderType?.toLowerCase(), ...data }),
    });

    if (!res.ok) {
      const errorData = await res.json(); // 👈 this parses the error body
      const errorMessage = errorData.detail || "Unknown error";
      console.error(errorMessage);
      setError(errorData.detail);
    } else {
      setError("");
      fetchPortfolioData();
      fetchPendingOrders();
    }
    reset();
  };

  return (
    <div className="bg-panel border border-divider rounded-md p-6 min-w-60 max-w-96 h-80 relative">
      <h1 className="mb-4 text-xl">Place Order</h1>

      <form
        className="flex flex-col"
        onSubmit={handleSubmit(handlePlaceOrderSubmit)}
      >
        <div>
          <input
            autoComplete="off"
            className={InputClass}
            type="text"
            {...register("symbol", {
              required: "Please enter symbol.",
            })}
            placeholder="Symbol"
          />
          <p className="text-error text-sm my-1 h-[1.25rem]">
            {errors?.price?.message ?? "\u00A0"}
          </p>
        </div>
        <div>
          <input
            type="number"
            className={InputClass}
            {...register("quantity", {
              required: "Please enter quantity",
              valueAsNumber: true,
              validate: (q) =>
                !(isNaN(q) || q <= 0) || "Must be a valid number",
            })}
            aria-invalid={errors.quantity ? "true" : "false"}
            placeholder="Quantity"
          />
          <p className="text-error text-sm my-1 h-[1.25rem]">
            {errors?.quantity?.message ?? "\u00A0"}
          </p>
        </div>
        <div>
          <input
            type="number"
            step="0.01"
            className={InputClass}
            {...register("price", {
              required: "Please enter limit price",
              valueAsNumber: true,
              validate: (p) => !(isNaN(p) || p <= 0) || "Must be a valid price",
            })}
            placeholder="Limit price"
            aria-invalid={errors.price ? "true" : "false"}
          />
          <p className="text-error text-sm my-1 h-[1.25rem]">
            {errors?.price?.message ?? "\u00A0"}
          </p>
        </div>
        <div className="px-6 pb-3 absolute bottom-0 right-0 w-full inline-flex justify-between gap-4">
          <button
            className="w-full py-1 h-8 px-4 border border-green-800 bg-green-600 hover:bg-green-700 duration-150 rounded-md hover:border-green-700 focus:outline-1 focus:outline-accent"
            onClick={onClick}
            type="submit"
          >
            Buy
          </button>

          <button
            className="w-full px-4 h-8 bg-error hover:bg-error-hover  duration-150 rounded-md focus:outline-1 focus:outline-accent"
            onClick={onClick}
            type="submit"
          >
            Sell
          </button>
        </div>
      </form>
      {error && <p className="text-red-600 mt-4 text-sm">{error}</p>}
    </div>
  );
};

export default PlaceOrderForm;
