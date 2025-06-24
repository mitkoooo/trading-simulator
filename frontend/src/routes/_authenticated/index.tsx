import { createFileRoute } from "@tanstack/react-router";
import { getTraderId } from "../../api/auth";
import { useEffect, useState } from "react";
import PortfolioEntry from "../../components/PortfolioEntry";
import { Position } from "../../types/domain";
import { getPositions } from "../../api/portfolio";

export const Route = createFileRoute("/_authenticated/")({ component: Index });

function Index() {
  const [traderId, setTraderId] = useState<null | number>(null);
  const [positions, setPositions] = useState<null | Position[]>(null);

  useEffect(() => {
    (async () => {
      const newTraderId = await getTraderId();
      setTraderId(newTraderId);
      const newPositions = await getPositions();
      setPositions(newPositions);
    })();
  }, []);

  const displayTraderId = () => (traderId === null ? "..." : traderId);

  return (
    <div className="p-2">
      <h3 className="mt-10 text-4xl">
        You are logged in as Trader {displayTraderId()}
        {positions &&
          positions.map((position) => (
            <PortfolioEntry
              className="mt-10"
              entry={position}
              key={position.ticket}
            ></PortfolioEntry>
          ))}
      </h3>
    </div>
  );
}
