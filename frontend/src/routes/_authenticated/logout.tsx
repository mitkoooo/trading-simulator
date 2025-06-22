import { createFileRoute, redirect } from "@tanstack/react-router";

const API_URL = "http://localhost:8000";

export const Route = createFileRoute("/_authenticated/logout")({
  component: Logout,
  beforeLoad: async () => {
    const res = await fetch(`${API_URL}/logout`, {
      method: "POST",
      credentials: "include",
    });
    console.log(res);
    // redirect the user to the login page
    throw redirect({ to: "/login" });
  },
});

function Logout() {
  return <></>;
}
