export interface Position {
  symbol: string;
  qty: number;
  avg_price: number;
}

export interface Portfolio {
  positions: Position[];
  cash: number;
  value: number;
  realizedPnL: number;
}

export interface Stock {
  symbol: string;
  history: [number, string][];
}

export interface Order {
  symbol: string;
  order_type: "buy" | "sell";
  quantity: number;
  limit_price?: number;
  order_id: string;
  status: string;
}

export interface OrderInfo {
  symbol: string;
  order_type: "buy" | "sell";
  fill_qty: number;
  avg_fill_price?: number;
  order_id: string;
  status: string;
  timestamp: string;
}

export interface Quote {
  symbol: string;
  bidPrice: number | null;
  bidSize: number | null;
  askPrice: number | null;
  askSize: number | null;
  lastPrice: number | null;
  dailyVol: number | null;
  timestamp: Date;
}

export type DataMap<T> = Record<string, T>;
