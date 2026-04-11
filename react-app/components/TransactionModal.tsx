/*
 * REACT PATTERN: Controlled modal with external open/close state
 *
 * The parent controls whether this modal is open via the `isOpen` prop,
 * and provides an `onClose` callback. This is preferable to the modal
 * managing its own visibility because the parent may need to trigger
 * side effects (like clearing the selected ticker) when the modal closes.
 *
 * We replaced react-modal's inline style objects with Tailwind classes
 * applied to a custom overlay + content wrapper. This gives us dark theme
 * support and responsive behavior without writing CSS.
 */

import React from "react";
import { Transaction } from "../types";
import LoadingSpinner from "./LoadingSpinner";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  ticker: string | null;
  transactions: Transaction[] | undefined;
  loading: boolean;
}

const TransactionModal: React.FC<Props> = ({
  isOpen,
  onClose,
  ticker,
  transactions,
  loading,
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content max-w-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Transactions &mdash;{" "}
            <span className="text-accent">{ticker}</span>
          </h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-terminal-muted transition-colors hover:bg-white/10 hover:text-white"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {loading ? (
          <LoadingSpinner label="Loading transactions..." />
        ) : !transactions?.length ? (
          <p className="py-8 text-center text-sm text-terminal-muted">
            No transactions found for {ticker}.
          </p>
        ) : (
          <div className="max-h-80 overflow-y-auto">
            <table className="w-full">
              <thead className="sticky top-0 bg-terminal-card">
                <tr className="border-b border-terminal-border">
                  <th className="table-header">Date</th>
                  <th className="table-header">Action</th>
                  <th className="table-header text-right">Volume</th>
                  <th className="table-header text-right">Price</th>
                  <th className="table-header text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-terminal-border">
                {transactions.map((tx, i) => (
                  <tr key={i} className="table-row-hover">
                    <td className="table-cell text-terminal-muted">
                      {new Date(tx.transaction_date).toLocaleDateString()}
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                          tx.action === "Buy"
                            ? "bg-bull/10 text-bull"
                            : "bg-bear/10 text-bear"
                        }`}
                      >
                        {tx.action}
                      </span>
                    </td>
                    <td className="table-cell text-right font-mono">{tx.volume}</td>
                    <td className="table-cell text-right font-mono">
                      ${Number(tx.close).toFixed(2)}
                    </td>
                    <td className="table-cell text-right font-mono">
                      ${Number(tx.total_transaction_amount).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default TransactionModal;
