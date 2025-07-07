import React from "react";
import { formatNumber } from "../utils/utils";

type CardProps = {
  children: React.JSX.Element[];
  className?: string;
}; /* use `interface` if exporting so that consumers can extend */

type CardTitleProps = {
  children: string | undefined;
};

type CardTotalProps = {
  children: number | undefined;
  currency: string;
  impact?: boolean;
};

const Card = ({ children, className }: CardProps): React.JSX.Element => {
  return (
    <div
      className={`${className} bg-card border-2 border-divider px-3 py-4 rounded-md`}
    >
      {children}
    </div>
  );
};

const Title = ({ children }: CardTitleProps): React.JSX.Element => {
  return children ? <h2 className="text-md">{children}</h2> : <></>;
};

const Total = ({
  children,
  currency,
  impact,
}: CardTotalProps): React.JSX.Element => {
  if (children === undefined) return <></>;

  const total = children;

  let changeColor = "text-primary";
  if (total > 0) changeColor = "text-success";
  else if (total < 0) changeColor = "text-error";

  const formattedChange = `${total > 0 && impact ? "+" : total < 0 ? "-" : ""}${currency}${formatNumber(Math.abs(total))}`;

  return (
    <p className={`text-3xl font-semibold ${impact ? changeColor : ""}`}>
      {formattedChange}
    </p>
  );
};

Card.Title = Title;
Card.Total = Total;

export default Card;
