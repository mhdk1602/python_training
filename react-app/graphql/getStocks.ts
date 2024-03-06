import { gql } from '@apollo/client';

export const GET_STOCKS = gql`
  query GetStocks {
    allStocks {
      nodes {
        ticker
        name
      }
    }
  }
`;
