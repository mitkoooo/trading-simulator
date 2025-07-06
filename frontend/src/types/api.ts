import type { DataMap, Position, Stock } from "./domain";

export interface MeResponse {
  trader_id: number;
}

export interface MePortfolioResponse {
  positions: Position[];
  cash: number;
  value: number;
  totalPnL: number;
}

export interface MarketDataResponse {
  market_data: DataMap<Stock>;
}
