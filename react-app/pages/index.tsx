/*
 * PAGE COMPONENT: Orchestrator pattern
 *
 * This file went from 800 lines to ~90 by applying component decomposition.
 * The page's only responsibilities are:
 *   1. Query data (Apollo GraphQL hooks)
 *   2. Manage which modal is open (local state)
 *   3. Compose child components and pass them the data they need
 *
 * All rendering logic, styling, and API interactions live in the
 * individual components and hooks under components/ and hooks/.
 *
 * LEARNING EXERCISE: Try adding a new feature (e.g., a watchlist)
 * by creating a new component and hook, then importing them here.
 */

import React, { useState, useEffect, useCallback } from "react";
import { useQuery } from "@apollo/client";
import { GET_STOCKS } from "../graphql/getStocks";
import { GET_PORTFOLIO_SUMMARY, GET_MAX_AS_OF_DATE } from "../graphql/getPortfolioSummaries";
import { GET_PORTFOLIO_TRANSACTIONS } from "graphql/getPortfolioTransactions";
import { useStockPrices } from "../hooks/useStockPrices";
import Layout from "../components/Layout";
import HoldingsTable from "../components/HoldingsTable";
import PortfolioSummary from "../components/PortfolioSummary";
import TransactionModal from "../components/TransactionModal";
import TradeModal from "../components/TradeModal";
import AskWarren from "../components/AskWarren";

const API_BASE = "http://localhost:5002";

const HomePage: React.FC = () => {
  const { data: stocksData, refetch: refetchStocks } = useQuery(GET_STOCKS);
  const { data: maxDateData, refetch: refetchMaxDate } = useQuery(GET_MAX_AS_OF_DATE);

  const [maxAsOfDate, setMaxAsOfDate] = useState<string | null>(null);
  useEffect(() => {
    if (maxDateData) {
      setMaxAsOfDate(maxDateData.portfolio_summary_aggregate.aggregate.max.as_of_date);
    }
  }, [maxDateData]);

  const { data: portfolioData, loading: portfolioLoading, refetch: refetchPortfolio } = useQuery(
    GET_PORTFOLIO_SUMMARY,
    { skip: !maxAsOfDate, variables: { maxAsOfDate } }
  );

  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const { data: txData, loading: txLoading } = useQuery(GET_PORTFOLIO_TRANSACTIONS, {
    skip: !selectedTicker,
    variables: { ticker: selectedTicker },
  });

  const { prices, directions, loading: pricesLoading } = useStockPrices(stocksData?.stocks);

  const [tradeType, setTradeType] = useState<"Buy" | "Sell" | null>(null);
  const [warrenOpen, setWarrenOpen] = useState(false);

  const refetchAll = useCallback(() => {
    refetchStocks();
    refetchMaxDate();
    refetchPortfolio();
  }, [refetchStocks, refetchMaxDate, refetchPortfolio]);

  useEffect(() => {
    fetch(`${API_BASE}/get-news`).catch(() => {});
    fetch(`${API_BASE}/populate_db`).catch(() => {});
  }, []);

  return (
    <Layout>
      <div className="grid gap-6 lg:grid-cols-2">
        <HoldingsTable
          stocks={stocksData?.stocks}
          prices={prices}
          directions={directions}
          loading={pricesLoading}
        />
        <PortfolioSummary
          data={portfolioData?.portfolio_summary}
          loading={portfolioLoading}
          onSelectTicker={setSelectedTicker}
        />
      </div>

      <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
        <button onClick={() => setTradeType("Buy")} className="btn-bull">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Buy
        </button>
        <button onClick={() => setTradeType("Sell")} className="btn-bear">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M20 12H4" />
          </svg>
          Sell
        </button>
        <button onClick={() => setWarrenOpen(true)} className="btn-primary">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          Ask Warren
        </button>
      </div>

      <TransactionModal
        isOpen={!!selectedTicker}
        onClose={() => setSelectedTicker(null)}
        ticker={selectedTicker}
        transactions={txData?.portfolio_transactions}
        loading={txLoading}
      />
      <TradeModal
        isOpen={!!tradeType}
        tradeType={tradeType}
        onClose={() => setTradeType(null)}
        onSuccess={refetchAll}
      />
      <AskWarren isOpen={warrenOpen} onClose={() => setWarrenOpen(false)} />
    </Layout>
  );
};

export default HomePage;
