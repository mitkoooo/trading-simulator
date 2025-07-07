export interface Position {
  symbol: string;
  qty: number;
  avg_price: number;
}

export interface Portfolio {
  positions: Position[];
  cash: number;
  value: number;
  totalPnL: number;
}

export interface Stock {
  symbol: string;
  price: number;
  volatility: number;
  history: number[];
}

export interface Order {
  trader_id: number;
  symbol: string;
  order_type: "buy" | "sell";
  quantity: number;
  limit_price?: number;
  order_id: string;
}

export type DataMap<T> = Record<string, T>;
