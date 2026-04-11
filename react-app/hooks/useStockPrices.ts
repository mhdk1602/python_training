/*
 * REACT PATTERN: Custom hook with polling interval
 *
 * This hook encapsulates the logic for fetching live stock prices on a
 * timer. By extracting it from the page component, we get:
 *   1. Reusability: any component can call useStockPrices(stocks)
 *   2. Testability: the hook can be tested without rendering UI
 *   3. Clean separation: the page only knows about prices, not HTTP calls
 *
 * Key concepts demonstrated:
 *   - useEffect cleanup: the returned function clears the interval
 *     to prevent memory leaks when the component unmounts
 *   - useRef for previous state: avoids stale closure problems
 *     that would occur with a second useState
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { Stock, StockPrices, PriceDirection } from "../types";

const POLL_INTERVAL_MS = 60_000;
const API_BASE = "http://localhost:5002";

export function useStockPrices(stocks: Stock[] | undefined) {
  const [prices, setPrices] = useState<StockPrices>({});
  const [directions, setDirections] = useState<Record<string, PriceDirection>>({});
  const [loading, setLoading] = useState(true);
  const prevPricesRef = useRef<StockPrices>({});

  const fetchPrices = useCallback(async () => {
    if (!stocks?.length) return;

    const incoming: StockPrices = {};
    await Promise.all(
      stocks.map(async (stock) => {
        try {
          const res = await fetch(
            `${API_BASE}/intraday-price?symbol=${stock.ticker}&interval=1m`
          );
          if (!res.ok) {
            incoming[stock.ticker] = "Error";
            return;
          }
          const data = await res.json();
          incoming[stock.ticker] = data.price ?? "N/A";
        } catch {
          incoming[stock.ticker] = "Error";
        }
      })
    );

    const prev = prevPricesRef.current;
    const dirs: Record<string, PriceDirection> = {};
    for (const ticker of Object.keys(incoming)) {
      const cur = incoming[ticker];
      const old = prev[ticker];
      if (typeof cur === "number" && typeof old === "number") {
        dirs[ticker] = cur > old ? "up" : cur < old ? "down" : "neutral";
      } else {
        dirs[ticker] = "neutral";
      }
    }

    prevPricesRef.current = incoming;
    setPrices(incoming);
    setDirections(dirs);
    setLoading(false);
  }, [stocks]);

  useEffect(() => {
    fetchPrices();
    const id = setInterval(fetchPrices, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [fetchPrices]);

  return { prices, directions, loading };
}
