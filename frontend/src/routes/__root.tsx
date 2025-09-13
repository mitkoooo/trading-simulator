import { createRootRoute, Outlet, useMatch } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import NavBar from "../components/nav/NavBar";

export const Route = createRootRoute({
  component: Root,
});

function Root(): React.JSX.Element {
  const isLoginPage = useMatch({ from: "/login", shouldThrow: false });

  return (
    <div className="bg-canvas text-primary flex min-h-dvh flex-col">
      {!isLoginPage && <NavBar />}
      <div className="flex min-h-0 flex-1 flex-col">
        <Outlet />
      </div>
      <TanStackRouterDevtools />
    </div>
  );
}
