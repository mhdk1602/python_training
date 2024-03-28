import { gql } from "@apollo/client";

export const GET_PORTFOLIO_TRANSACTIONS = gql`
  query GetPortfolioTransactions($ticker: String!) {
    portfolio_transactions(where: { ticker: { _eq: $ticker } }) {
      transaction_date
      action
      volume
      close
      total_transaction_amount
      stock {
        name
      }
    }
  }
`;
