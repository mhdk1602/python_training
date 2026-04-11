/*
 * REACT PATTERN: Click-to-drill interaction
 *
 * This table renders portfolio summary rows. When a user clicks a row,
 * it calls onSelectTicker(ticker) which the parent uses to open a
 * TransactionModal. This "callback prop" pattern keeps the summary
 * component unaware of modals entirely, following the principle of
 * lifting state up to the nearest common ancestor.
 */

import React from "react";
import { PortfolioSummaryItem } from "../types";
import LoadingSpinner from "./LoadingSpinner";
import EmptyState from "./EmptyState";

interface Props {
  data: PortfolioSummaryItem[] | undefined;
  loading: boolean;
  onSelectTicker: (ticker: string) => void;
}

const PortfolioSummary: React.FC<Props> = ({ data, loading, onSelectTicker }) => {
  if (loading) return <LoadingSpinner label="Loading portfolio..." />;

  return (
    <div className="card">
      <h2 className="mb-4 flex items-center gap-2 text-base font-semibold text-white">
        <svg className="h-5 w-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
        Portfolio Summary
      </h2>
      {!data?.length ? (
        <EmptyState
          title="No positions yet"
          message="Use the Buy button to make your first trade."
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-terminal-border">
                <th className="table-header">Ticker</th>
                <th className="table-header">Name</th>
                <th className="table-header text-right">Shares</th>
                <th className="table-header text-right">Value</th>
                <th className="table-header text-right">As Of</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-terminal-border">
              {data.map((item) => (
                <tr
                  key={item.ticker}
                  className="table-row-hover"
                  onClick={() => onSelectTicker(item.ticker)}
                >
                  <td className="table-cell font-mono font-medium text-accent">
                    {item.ticker}
                  </td>
                  <td className="table-cell">{item.stock.name}</td>
                  <td className="table-cell text-right font-mono">
                    {item.total_shares}
                  </td>
                  <td className="table-cell text-right font-mono">
                    {item.total_asset_value != null
                      ? `$${Number(item.total_asset_value).toFixed(2)}`
                      : "N/A"}
                  </td>
                  <td className="table-cell text-right text-terminal-muted">
                    {new Date(item.as_of_date).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default PortfolioSummary;
