import { gql } from "@apollo/client";

export const GET_MAX_AS_OF_DATE = gql`
  query GetMaxAsOfDate {
    portfolio_summary_aggregate {
      aggregate {
        max {
          as_of_date
        }
      }
    }
  }
`;

export const GET_PORTFOLIO_SUMMARY = gql`
  query GetPortfolioSummary($maxAsOfDate: timestamp!) {
    portfolio_summary(where: { as_of_date: { _eq: $maxAsOfDate } }) {
      ticker
      total_shares
      total_asset_value
      as_of_date
      stock {
        name
      }
    }
  }
`;
