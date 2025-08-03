import { useEffect, useState } from "react";
import { usePortfolioDataStore } from "../../stores/portfolioDataStore";

import { Cross } from "../../assets/cross";

import { LoaderPinwheel } from "lucide-react";

import toast, { type Toast } from "react-hot-toast";
import { postCancelOrder } from "../../api/trader";

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
			<h1 className="mb-2 text-xl">Your pending orders</h1>
			{pendingOrders.length !== 0 ? (
				<div
					className="bg-panel border-divider flex flex-col rounded-md border"
					onClick={handleContainerClick}
				>
					{pendingOrders?.map((o, i) => (
						<div
							className={`inline-flex w-full justify-between p-3 ${i !== pendingOrders.length - 1 ? "" : "border-b"} border-divider items-center`}
							key={o.order_id}
						>
							<div className="inline-flex gap-4">
								<span className="font-semibold">
									{o.order_type.toUpperCase()}
								</span>
								<span>{o.symbol}</span>
								<span className="font-mono">{o.limit_price ?? "MARKET"}</span>
								<span>{o.quantity}</span>
							</div>
							<button data-order-id={o.order_id}>
								<Cross className="text-error hover:text-error-hover h-8 min-h-8 w-8 min-w-8" />
							</button>
						</div>
					))}
				</div>
			) : (
				<p className="text-md flex items-center justify-center">
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
			className={`${t.visible ? "animate-enter" : "animate-leave"} bg-card text-primary border-divider pointer-events-auto w-full max-w-md flex-col rounded-lg border-2 p-3 shadow-lg`}
		>
			{toastState === "ready" && (
				<>
					<p className="mb-4 text-center">
						Are you sure you want to cancel your order(s)?
					</p>
					<div className="inline-flex w-full justify-between gap-8">
						<button
							className="bg-success text-primary bg-panel hover:bg-success-hover w-full rounded-lg"
							onClick={onSuccess}
						>
							Yes
						</button>
						<button
							className="bg-error text-primary hover:bg-error-hover w-full rounded-lg"
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
