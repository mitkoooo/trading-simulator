type PlaceOrderButtonProps = {
	currentState: {
		currentSide: "buy" | "sell";
		currentSymbol: string | null;
		currentQuantity: number | null;
		currentPrice: number | null;
	};
};

const PlaceOrderButton = ({
	currentState: { currentSide, currentQuantity, currentSymbol, currentPrice },
}: PlaceOrderButtonProps): React.JSX.Element => {
	const SellCSS = "bg-error hover:bg-error-hover";
	const BuyCSS = "bg-green-600 hover:bg-green-700";

	const formattedAction =
		currentSide?.slice(0, 1).toUpperCase() + currentSide?.slice(1);
	const formattedPrice = currentPrice
		? String(Number(currentPrice)?.toFixed(2))
		: "";

	return (
		<button
			className={`w-full p-3 ${currentSide === "sell" ? SellCSS : BuyCSS} focus:outline-accent w-full rounded-md duration-150 focus:outline-1`}
			type="submit"
		>
			{formattedAction} {currentQuantity ? currentQuantity + " " : ""}
			{currentSymbol ? currentSymbol : "..."}@$
			{formattedPrice}
		</button>
	);
};

export default PlaceOrderButton;
