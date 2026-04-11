/*
 * REACT PATTERN: Props and data mapping
 *
 * This component demonstrates one of the most common React patterns:
 * receiving an array via props and mapping it to table rows. Key ideas:
 *
 *   1. The component does not fetch data. It receives stocks, prices,
 *      and directions as props from the parent page.
 *   2. Each row uses stock.ticker as the React key, which is stable
 *      and unique (important for efficient re-renders).
 *   3. PriceCell is a child component that handles its own styling.
 *      This keeps HoldingsTable focused on layout, not color logic.
 */

import React from "react";
import { Stock, StockPrices, PriceDirection } from "../types";
import PriceCell from "./PriceCell";
import LoadingSpinner from "./LoadingSpinner";

interface Props {
  stocks: Stock[] | undefined;
  prices: StockPrices;
  directions: Record<string, PriceDirection>;
  loading: boolean;
}

const HoldingsTable: React.FC<Props> = ({ stocks, prices, directions, loading }) => {
  if (loading) return <LoadingSpinner label="Fetching prices..." />;
  if (!stocks?.length) return null;

  return (
    <div className="card">
      <h2 className="mb-4 flex items-center gap-2 text-base font-semibold text-white">
        <svg className="h-5 w-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
        Holdings
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-terminal-border">
              <th className="table-header">Ticker</th>
              <th className="table-header">Name</th>
              <th className="table-header text-right">Price</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-terminal-border">
            {stocks.map((stock) => (
              <tr key={stock.ticker} className="table-row-hover">
                <td className="table-cell font-mono font-medium text-accent">
                  {stock.ticker}
                </td>
                <td className="table-cell">{stock.name}</td>
                <td className="table-cell text-right">
                  <PriceCell
                    value={prices[stock.ticker] ?? "N/A"}
                    direction={directions[stock.ticker] ?? "neutral"}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default HoldingsTable;
