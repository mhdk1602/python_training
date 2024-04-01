import { ApolloClient, InMemoryCache } from '@apollo/client';

const apolloClient = new ApolloClient({
  uri: 'http://localhost:8080/v1/graphql', // Using environment variable for endpoint
  headers: {
    'x-hasura-admin-secret': 'mWNAnrNoFvIVZxg2j6XqRL3TGHWuvQ0TK2UmvfNy8o8haVTaf3y7X6ch02qIlu2G' ?? '', // Using environment variable for admin secret with default value
  },
  cache: new InMemoryCache(),
});

export default apolloClient;