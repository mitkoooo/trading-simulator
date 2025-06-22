import {
  createRootRoute,
  Link,
  Outlet,
  useMatch,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

export const Route = createRootRoute({
  component: () => {
    const isLoginPage = useMatch({ from: "/login", shouldThrow: false });

    return (
      <>
        {!isLoginPage && (
          <>
            <div className="p-2 flex gap-2">
              <Link to="/" className="[&.active]:font-bold">
                Home
              </Link>
              <Link to="/about" className="[&.active]:font-bold">
                About
              </Link>
              <Link to="/logout" className="[&.active]:font-bold">
                Log out
              </Link>
            </div>
            <hr />
          </>
        )}
        <Outlet />
        <TanStackRouterDevtools />
      </>
    );
  },
});
