/*
 * TYPESCRIPT PATTERN: Centralized type definitions
 *
 * Defining shared interfaces in one place prevents drift between
 * components that consume the same data. These types mirror the
 * GraphQL schema exposed by Hasura, so when the schema changes
 * you update one file and the compiler flags every affected component.
 */

export interface Stock {
  ticker: string;
  name: string;
}

export interface PortfolioSummaryItem {
  ticker: string;
  total_shares: number;
  total_asset_value: number | null;
  as_of_date: string;
  stock: { name: string };
}

export interface Transaction {
  transaction_date: string;
  action: string;
  volume: number;
  close: number;
  total_transaction_amount: number;
  stock: { name: string };
}

export interface ChatMessage {
  role: "user" | "warren";
  content: string;
}

export type PriceDirection = "up" | "down" | "neutral";

export interface StockPrices {
  [ticker: string]: number | "N/A" | "Error";
}
