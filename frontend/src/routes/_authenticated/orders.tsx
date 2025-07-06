import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/orders")({
  component: Orders,
});

function Orders() {
  return <div className="p-2">Hello from Orders!</div>;
}
