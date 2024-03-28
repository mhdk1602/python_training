import { ApolloClient, InMemoryCache } from '@apollo/client';

const apolloClient = new ApolloClient({
  uri: 'http://localhost:8080/v1/graphql', // Using environment variable for endpoint
  headers: {
    'x-hasura-admin-secret': 'YOUR_HASURA_ADMIN_SECRET' ?? '', // Using environment variable for admin secret with default value
  },
  cache: new InMemoryCache(),
});

export default apolloClient;