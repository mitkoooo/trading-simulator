import type { DataMap, Position, Stock } from "./domain";

export interface MeResponse {
  trader_id: number;
}

export interface MePortfolioResponse {
  portfolio: {
    positions: DataMap<Position>;
    cash: number;
    value: number;
  };
}

export interface MarketDataResponse {
  market_data: DataMap<Stock>;
}
