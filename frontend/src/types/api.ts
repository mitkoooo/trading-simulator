import type { Position } from "./domain";

export interface MeResponse {
  trader_id: string;
}

export interface PortfolioResponse {
  status: number;
  positions: Position[];
  cash: number;
  value: number;
  total_pnl: number;
}
