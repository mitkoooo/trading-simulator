import { useForm, type SubmitHandler } from "react-hook-form";

import { API_BASE } from "../config/api";
import { useState } from "react";

type PlaceOrderFormProps = {
  onOrderVisible: unknown;
  orderType: string | null;
}; /* use `interface` if exporting so that consumers can extend */

interface PlaceOrderFormData {
  symbol: string;
  quantity: number;
  price: number;
}

const PlaceOrderForm = ({
  onOrderVisible,
  orderType,
}: PlaceOrderFormProps): React.JSX.Element => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PlaceOrderFormData>();

  const [error, setError] = useState<string | null>(null);

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
      onOrderVisible(false);
    }
  };

  return (
    <div>
      <form
        className="flex flex-col w-40"
        onSubmit={handleSubmit(handlePlaceOrderSubmit)}
      >
        <button onClick={() => onOrderVisible(false)}>Close form</button>
        <p className="mb-2">Order type: {orderType?.toUpperCase()}</p>
        <div>
          <label htmlFor="symbol" className="block mb-1">
            Symbol
          </label>
          <input
            className="bg-gray-100 border rounded-md text-black"
            type="text"
            {...register("symbol", {
              required: "Please enter symbol.",
            })}
            placeholder="Enter symbol"
          />
        </div>
        <div>
          <label htmlFor="quantity" className="block mb-1">
            Quantity
          </label>
          <input
            type="number"
            className="bg-gray-100 border rounded-md text-black"
            {...register("quantity", {
              required: "Please enter quantity.",
              valueAsNumber: true,
              validate: (q) =>
                !(isNaN(q) || q <= 0) || "Must be a valid number",
            })}
            aria-invalid={errors.quantity ? "true" : "false"}
            placeholder="Enter quantity"
          />
          {errors.quantity && (
            <p className="text-red-600 text-sm mt-1 ">
              {errors.quantity.message}
            </p>
          )}
        </div>
        <div>
          <label htmlFor="price" className="block mb-1">
            Limit price
          </label>
          <input
            type="number"
            step="0.001"
            className="bg-gray-100 border rounded-md text-black"
            {...register("price", {
              required: "Please enter limit price",
              valueAsNumber: true,
              validate: (p) => !(isNaN(p) || p <= 0) || "Must be a valid price",
            })}
            placeholder="Enter limit price"
            aria-invalid={errors.price ? "true" : "false"}
          />
          {errors.price && (
            <p className="text-red-600 text-sm mt-1 ">{errors.price.message}</p>
          )}
        </div>
        <input
          className="mt-4 py-1 h-8 px-4 bg-blue-800 border border-blue-950 duration-150 rounded-md"
          type="submit"
          value={"Place order"}
        />
      </form>
      {error && <p className="text-red-600 mt-1 text-sm">{error}</p>}
    </div>
  );
};

export default PlaceOrderForm;
