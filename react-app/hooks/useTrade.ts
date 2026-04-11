/*
 * REACT PATTERN: Async action hook with state machine
 *
 * Trade execution involves three distinct UI states:
 *   idle -> loading -> success | error
 *
 * Rather than scattering useState calls across a component, this hook
 * manages the entire lifecycle and exposes a clean API:
 *   const { execute, status, feedback, reset } = useTrade(onSuccess)
 *
 * The onSuccess callback lets the parent trigger GraphQL refetches
 * without the hook needing to know about Apollo.
 */

import { useState, useCallback } from "react";

const API_BASE = "http://localhost:5002";

type TradeStatus = "idle" | "loading" | "success" | "error";

interface TradeParams {
  symbol: string;
  volume: number;
  trade_type: "Buy" | "Sell";
}

export function useTrade(onSuccess?: () => void) {
  const [status, setStatus] = useState<TradeStatus>("idle");
  const [feedback, setFeedback] = useState<string | null>(null);

  const execute = useCallback(
    async (params: TradeParams) => {
      if (!params.symbol || !params.volume) {
        setStatus("error");
        setFeedback("Please enter a valid stock ticker and volume.");
        return;
      }

      setStatus("loading");
      setFeedback(null);

      try {
        const res = await fetch(`${API_BASE}/trade`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(params),
        });
        const result = await res.json();

        if (result.error) {
          setStatus("error");
          setFeedback(result.error);
        } else {
          setStatus("success");
          setFeedback(result.message);
          onSuccess?.();
        }
      } catch (err: unknown) {
        setStatus("error");
        setFeedback(err instanceof Error ? err.message : "Trade failed");
      }
    },
    [onSuccess]
  );

  const reset = useCallback(() => {
    setStatus("idle");
    setFeedback(null);
  }, []);

  return { execute, status, feedback, reset };
}
