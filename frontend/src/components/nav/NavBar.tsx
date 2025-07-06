import { useEffect, useState } from "react";
import { getTraderId } from "../../api/auth";
import Logo from "./Logo";
import { Link } from "@tanstack/react-router";

const LinkClass =
  "text-xl text-nav-inactive [&.active]:border-b-2 border-accent [&.active]:text-nav-active hover:text-nav-hover";

const NavBar = (): React.JSX.Element => {
  const [traderId, setTraderId] = useState<null | number>(null);

  useEffect(() => {
    (async () => {
      const newTraderId = await getTraderId();
      setTraderId(newTraderId);
    })();
  }, []);

  return (
    <>
      <div className="sticky top-0 z-50 flex items-center justify-center py-3 px-6 bg-panel border-2 border-divider h-16">
        <Logo className="absolute left-4" />
        <div className=" flex gap-4">
          <Link to="/" className={LinkClass}>
            Portfolio
          </Link>
          <Link to="/orders" className={LinkClass}>
            Orders
          </Link>
        </div>
        <div className="flex gap-8 absolute text-xl right-8">
          <span className="text-info select-none">Trader {traderId}</span>
          <Link
            className="text-xl text-error hover:text-error-hover rounded-md"
            to="/logout"
          >
            Log out
          </Link>
        </div>
      </div>
    </>
  );
};

export default NavBar;
