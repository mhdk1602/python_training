import { gql } from "@apollo/client";

export const GET_PORTFOLIO_TRANSACTIONS = gql`
  query GetPortfolioTransactions($ticker: String!) {
    allPortfolioTransactions(condition: {ticker: $ticker}) {
      nodes {
        transactionDate
        action
        volume
        close
        totalTransactionAmount
        stockByTicker {
          name
        }
      }
    }
  }
`;
