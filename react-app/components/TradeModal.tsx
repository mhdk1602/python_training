/*
 * REACT PATTERN: Controlled form with two-way binding
 *
 * This modal demonstrates the "controlled component" pattern for forms:
 *   - Each input's value is tied to a useState variable
 *   - Each onChange handler updates that variable
 *   - On submit, the current state is passed to the useTrade hook
 *
 * The form also shows:
 *   - Conditional rendering of feedback messages (success/error)
 *   - Disabling the submit button during loading to prevent double-submit
 *   - Resetting form state when the modal closes
 */

import React, { useState, useEffect } from "react";
import { useTrade } from "../hooks/useTrade";

interface Props {
  isOpen: boolean;
  tradeType: "Buy" | "Sell" | null;
  onClose: () => void;
  onSuccess: () => void;
}

const TradeModal: React.FC<Props> = ({ isOpen, tradeType, onClose, onSuccess }) => {
  const [ticker, setTicker] = useState("");
  const [volume, setVolume] = useState("");
  const { execute, status, feedback, reset } = useTrade(onSuccess);

  useEffect(() => {
    if (!isOpen) {
      setTicker("");
      setVolume("");
      reset();
    }
  }, [isOpen, reset]);

  if (!isOpen || !tradeType) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    execute({
      symbol: ticker.toUpperCase(),
      volume: Number(volume),
      trade_type: tradeType,
    });
  };

  const isBuy = tradeType === "Buy";

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content max-w-md" onClick={(e) => e.stopPropagation()}>
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            {tradeType} Stock
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

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-terminal-muted">
              Ticker Symbol
            </label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="e.g. AAPL"
              className="input-field font-mono uppercase"
              autoFocus
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-terminal-muted">
              Number of Shares
            </label>
            <input
              type="number"
              min="1"
              value={volume}
              onChange={(e) => setVolume(e.target.value)}
              placeholder="e.g. 10"
              className="input-field font-mono"
            />
          </div>

          <button
            type="submit"
            disabled={status === "loading"}
            className={`w-full ${isBuy ? "btn-bull" : "btn-bear"} justify-center ${
              status === "loading" ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {status === "loading" ? (
              <>
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
                Executing...
              </>
            ) : (
              `${tradeType} Shares`
            )}
          </button>
        </form>

        {feedback && (
          <div
            className={`mt-4 rounded-lg border px-3 py-2 text-sm ${
              status === "success"
                ? "border-bull/30 bg-bull/10 text-bull"
                : "border-bear/30 bg-bear/10 text-bear"
            }`}
          >
            {feedback}
          </div>
        )}
      </div>
    </div>
  );
};

export default TradeModal;
