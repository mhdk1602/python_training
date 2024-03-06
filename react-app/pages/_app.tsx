import { ApolloProvider } from '@apollo/client';
import apolloClient from 'apollo-client';  // adjust the path as necessary
import type { AppProps } from 'next/app';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ApolloProvider client={apolloClient}>
      <Component {...pageProps} />
    </ApolloProvider>
  );
}

export default MyApp;
