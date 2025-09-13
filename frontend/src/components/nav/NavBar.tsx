import { useEffect, useState } from "react";
import { getTraderId } from "../../api/auth";
import Logo from "./Logo";
import { Link } from "@tanstack/react-router";

const LinkClass =
  "text-lg text-nav-inactive [&.active]:border-b border-accent [&.active]:text-nav-active hover:text-nav-hover";

const NavBar = (): React.JSX.Element => {
  const [traderId, setTraderId] = useState<null | string>(null);

  useEffect(() => {
    (async () => {
      const newTraderId = await getTraderId();
      setTraderId(newTraderId);
    })();
  }, []);

  return (
    <>
      <div className="bg-panel border-divider sticky top-0 z-50 flex h-8 items-center justify-center border px-1 py-1">
        <Logo className="absolute left-2" />
        {/*
        <div className="flex gap-4">
          <Link to="/" className={LinkClass}>
            Dashboard
          </Link>
          <Link to="/orders" className={LinkClass}>
            Portfolio
          </Link>
        </div>
	*/}
        <div className="text-md absolute right-4 flex gap-8">
          <span className="text-info select-none">TRADER {traderId}</span>
          <Link
            className="text-error hover:text-error-hover rounded-md"
            to="/logout"
          >
            LOGOUT
          </Link>
        </div>
      </div>
    </>
  );
};

export default NavBar;
