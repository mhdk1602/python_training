import { ApolloClient, InMemoryCache } from '@apollo/client';

const graphqlUri =
  process.env.REACT_APP_HASURA_GRAPHQL_URL || 'http://localhost:8080/v1/graphql';
const hasuraAdminSecret = process.env.REACT_APP_HASURA_ADMIN_SECRET || '';

const apolloClient = new ApolloClient({
  uri: graphqlUri,
  headers: hasuraAdminSecret ? { 'x-hasura-admin-secret': hasuraAdminSecret } : {},
  cache: new InMemoryCache(),
});

export default apolloClient;