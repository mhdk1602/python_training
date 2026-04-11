/*
 * REACT PATTERN: Conditional styling with derived state
 *
 * This component receives a price value and a direction ("up", "down",
 * or "neutral") and renders it with the appropriate color and a brief
 * flash animation. The animation class is applied on direction change
 * via Tailwind's custom keyframes defined in tailwind.config.ts.
 *
 * Notice that the component is pure: it takes props and returns JSX.
 * The parent (HoldingsTable) decides what direction to pass based on
 * the previous vs. current price comparison in useStockPrices.
 */

import React from "react";
import { PriceDirection } from "../types";

interface Props {
  value: number | string;
  direction: PriceDirection;
}

const directionStyles: Record<PriceDirection, string> = {
  up: "text-bull animate-flash-green",
  down: "text-bear animate-flash-red",
  neutral: "text-terminal-text",
};

const PriceCell: React.FC<Props> = ({ value, direction }) => {
  const formatted =
    typeof value === "number" ? `$${value.toFixed(2)}` : String(value);

  return (
    <span className={`font-mono text-sm tabular-nums transition-colors ${directionStyles[direction]}`}>
      {formatted}
    </span>
  );
};

export default PriceCell;
