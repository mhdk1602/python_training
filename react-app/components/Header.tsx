/*
 * REACT PATTERN: Presentational component
 *
 * This component has no state or side effects. It receives no props and
 * renders pure markup. In a larger app you would pass navigation items
 * or user info as props. Keeping the header stateless makes it easy to
 * test and reuse across pages.
 */

import Link from "next/link";
import React from "react";

const Header: React.FC = () => {
  return (
    <header className="border-b border-terminal-border bg-terminal-card">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-sm font-bold text-white">
            ST
          </div>
          <h1 className="text-lg font-semibold text-white">
            Stock Trading Platform
          </h1>
        </div>
        <div className="flex items-center gap-4 text-xs text-terminal-muted">
          <Link href="/chapter-10" className="text-accent hover:text-white transition-colors">
            Chapter 10 Lab
          </Link>
          <div className="flex items-center gap-2">
            <span className="inline-block h-2 w-2 rounded-full bg-bull animate-pulse-slow" />
            Market Live
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
