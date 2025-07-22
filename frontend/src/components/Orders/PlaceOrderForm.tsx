import { Controller, useForm, type SubmitHandler } from "react-hook-form";

import { API_BASE } from "../../config/api";
import { useState } from "react";
import { usePortfolioDataStore } from "../../stores/portfolioDataStore";
import { useMarketDataStore } from "../../stores/marketDataStore";

import PlaceOrderButton from "./PlaceOrderButton.tsx";

interface PlaceOrderFormData {
	orderSide: "buy" | "sell";
	orderType: "market" | "limit";
	symbol: string;
	quantity: number | null;
	price: number | null;
}

const InputClass =
	"px-2 py-1 bg-card border-2 rounded-md text-primary border-divider focus:bg-card focus:outline-1 focus:outline-accent";

const PlaceOrderForm = (): React.JSX.Element => {
	const {
		control,
		register,
		reset,
		handleSubmit,
		watch,
		setValue,
		formState: { errors },
	} = useForm<PlaceOrderFormData>({
		defaultValues: {
			orderSide: "buy",
			orderType: "market",
			symbol: "",
			quantity: null,
			price: null,
		},
	});

	const fetchPortfolioData = usePortfolioDataStore(
		(state) => state.fetchPortfolioData,
	);
	const fetchPendingOrders = usePortfolioDataStore(
		(state) => state.fetchPendingOrders,
	);

	const getMarketPrice = useMarketDataStore((state) => state.getMarketPrice);

	const [apiError, setApiError] = useState<string | null>(null);
	// watch keeps the latest value of price in sync
	const currentSide = watch("orderSide");
	const currentType = watch("orderType");
	const currentPrice =
		currentType === "market"
			? getMarketPrice(watch("symbol"))?.price || null
			: watch("price") || null;
	const currentSymbol = watch("symbol");
	const currentQuantity = watch("quantity");

	const changeOnePercent = (direction: "+" | "-") => {
		if (!currentPrice) return;
		if (!direction || (direction !== "+" && direction !== "-")) return;
		const percentageChange = direction === "+" ? 1.01 : 0.99;

		const newPrice = (currentPrice * percentageChange).toFixed(2);
		// imperatively write that back into the form state
		setValue("price", parseFloat(newPrice), {
			shouldValidate: true,
			shouldDirty: true,
		});
	};

	const handlePlaceOrderSubmit: SubmitHandler<PlaceOrderFormData> = async (
		data: PlaceOrderFormData,
	) => {
		const body = {
			order_type: data.orderSide.toLowerCase(),
			symbol: data.symbol,
			quantity: data.quantity,
			price: data.price,
		};

		setApiError("");
		const res = await fetch(`${API_BASE}/order`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(body),
		});

		if (!res.ok) {
			const errorData = await res.json(); // 👈 this parses the error body
			const errorMessage = errorData.detail || "Unknown error";
			console.error(errorMessage);
			setApiError(errorMessage);
		} else {
			await fetchPortfolioData();
			await fetchPendingOrders();
		}
		reset({
			orderType: "market",
			orderSide: "buy",
			symbol: "",
			quantity: null,
			price: null,
		});
	};

	return (
		<div className="bg-panel border-divider relative max-w-96 min-w-80 rounded-sm border p-8">
			<form
				className="flex flex-col"
				onSubmit={handleSubmit(handlePlaceOrderSubmit)}
			>
				<div className="mb-4 inline-flex w-full">
					<input
						type="button"
						value={"Buy"}
						className={`w-full rounded-l-sm p-1 transition-colors duration-100 ${currentSide === "sell" ? "bg-disabled hover:bg-gray-700" : "bg-green-600"}`}
						onClick={() => setValue("orderSide", "buy")}
					/>
					<input
						type="button"
						value={"Sell"}
						className={`w-full rounded-r-sm p-1 transition-all duration-100 ${currentSide === "buy" ? "bg-disabled hover:bg-gray-700" : "bg-error"}`}
						onClick={() => setValue("orderSide", "sell")}
					/>
				</div>
				<div className="infline-flex mb-2 w-full items-center justify-start">
					<input
						type="button"
						value={"Market"}
						className={`border-divider mr-4 w-16 p-2 text-sm focus:outline-none ${currentType === "market" ? "bg-zinc-800" : "bg-card"}`}
						onClick={() => {
							setValue("price", null);
							setValue("orderType", "market");
						}}
					/>
					<input
						type="button"
						value={"Limit"}
						className={`bg-card border-divider w-16 p-2 text-sm focus:outline-none ${currentType === "limit" ? "bg-zinc-800" : "bg-card"}`}
						onClick={() => setValue("orderType", "limit")}
					/>
				</div>
				<p
					className={`text-secondary mb-2 text-xs ${currentType === "market" ? "" : "opacity-0"}`}
				>
					Executes immediately at best price.
				</p>

				{/* ── Symbol ── */}
				<div>
					<input
						autoComplete="off"
						className={`${InputClass} w-full`}
						type="text"
						{...register("symbol", {
							required: "Please enter symbol.",
							onChange: () => setApiError(""),
						})}
						placeholder="Symbol"
					/>
					<p className="text-error my-1 h-[1.25rem] text-sm">
						{errors?.symbol?.message ?? "\u00A0"}
					</p>
				</div>
				{/* ── Quantity ── */}
				<div>
					<input
						autoComplete="off"
						className={`${InputClass} w-full`}
						{...register("quantity", {
							required: "Please enter quantity",
							valueAsNumber: true,
							validate: (q) =>
								!(isNaN(q) || q <= 0) || "Must be a valid number",
							onChange: () => setApiError(""),
						})}
						aria-invalid={errors.quantity ? "true" : "false"}
						placeholder="Quantity"
					/>
					<p className="text-error my-1 h-[1.25rem] text-sm">
						{errors?.quantity?.message ?? "\u00A0"}
					</p>
				</div>
				{/* ── Price ── */}
				<div
					className={`transition‐all duration‐200 overflow‐hidden ${currentType === "market" ? "h-0 opacity-0" : "h-auto"}`}
				>
					<div className="inline-flex justify-between gap-4">
						<Controller
							name="price"
							control={control}
							rules={{
								// only required when it's a limit order
								required:
									currentType === "limit" ? "Please enter limit price" : false,
								validate: (v) =>
									currentType === "limit"
										? (v !== null && v > 0) || "Please enter valid limit price"
										: true,
							}}
							render={({ field }) => {
								const safeValue = field.value ?? "";
								return (
									<input
										autoComplete="off"
										type="number"
										step="0.01"
										className={`w-full min-w-12 ${InputClass}`}
										{...field}
										value={safeValue}
										disabled={currentType === "market"}
										placeholder="Limit price"
										aria-invalid={errors.price ? "true" : "false"}
									/>
								);
							}}
						/>
						<div className="inline-flex w-auto justify-between gap-2">
							<button
								type="button"
								className="bg-card border-divider focus:outline-accent px-2 text-sm focus:outline-1"
								onClick={() => changeOnePercent("+")}
							>
								+1%
							</button>
							<button
								type="button"
								className="bg-card border-divider focus:outline-accent px-2 text-sm focus:outline-1"
								onClick={() => changeOnePercent("-")}
							>
								-1%
							</button>
						</div>
					</div>

					<p className="text-error my-1 h-[1.25rem] text-sm">
						{errors?.price?.message ?? "\u00A0"}
					</p>
				</div>
				{apiError && (
					<p className="text-error h-[1.25rem] text-sm">{apiError}</p>
				)}
				<div className="absolute right-0 bottom-10 left-0 mx-12 inline-flex">
					<PlaceOrderButton
						currentState={{
							currentSide: currentSide,
							currentQuantity: currentQuantity,
							currentSymbol: currentSymbol,
							currentPrice: currentPrice,
						}}
					/>
				</div>
			</form>
		</div>
	);
};

export default PlaceOrderForm;
