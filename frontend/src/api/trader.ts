import { API_BASE } from "../config/api";

export async function postOrder(
  symbol: string,
  order_type: "buy" | "sell",
  quantity: number,
  price?: number,
): Promise<boolean> {
  const order = { symbol, order_type, quantity, price };

  try {
    const res = await fetch(`${API_BASE}/orders`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(order),
    });

    if (!res.ok) {
      throw new Error(`Couldn't place the order (${res.status})`);
    }

    return res.ok;
  } catch (err) {
    console.error(err);
    throw err;
  }
}

export async function postCancelOrder(order_id: string): Promise<boolean> {
  const body = { order_id };
  try {
    const res = await fetch(`${API_BASE}/orders/${order_id}`, {
      method: "DELETE",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      throw new Error(`Couldn't cancel the order (${res.status})`);
    }
    console.log(res.json());
    return res.ok;
  } catch (err) {
    console.error(err);
    throw err;
  }
}
