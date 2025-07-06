import { createRootRoute, Outlet, useMatch } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import NavBar from "../components/nav/NavBar";

export const Route = createRootRoute({
  component: Root,
});

function Root(): React.JSX.Element {
  const isLoginPage = useMatch({ from: "/login", shouldThrow: false });

  return (
    <>
      {!isLoginPage && <NavBar />}
      <Outlet />
      <TanStackRouterDevtools />
    </>
  );
}
