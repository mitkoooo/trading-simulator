import type { Position } from "./domain";

export interface MeResponse {
  trader_id: number;
}

export interface MePortfolioResponse {
  positions: Position[];
}
