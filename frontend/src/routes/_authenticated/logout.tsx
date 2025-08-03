import { createFileRoute, redirect } from "@tanstack/react-router";
import { API_BASE } from "../../config/api";

export const Route = createFileRoute("/_authenticated/logout")({
  component: Logout,
  beforeLoad: async () => {
    await fetch(`${API_BASE}/users/logout`, {
      method: "POST",
      credentials: "include",
    });
    // redirect the user to the login page
    throw redirect({ to: "/login" });
  },
});

function Logout() {
  return <></>;
}
