import { gql } from "@apollo/client";

export const GET_PORTFOLIO_SUMMARY = gql`
  query GetPortfolioSummary {
    allPortfolioSummaries {
      nodes {
        ticker
        totalShares
        totalAssetValue
        asOfDate
        stockByTicker {
          name
        }
      }
    }
  }
`;