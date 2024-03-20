const express = require('express');
const { execute, subscribe } = require('graphql');
const { SubscriptionServer } = require('subscriptions-transport-ws');
const { makeExecutableSchema } = require('@graphql-tools/schema');
const { graphqlHTTP } = require('express-graphql');
const { PubSub } = require('graphql-subscriptions');
const typeDefs = require('./schema');
const resolvers = require('./resolvers');
const http = require('http');

const pubsub = new PubSub();
const schema = makeExecutableSchema({ typeDefs, resolvers });
const app = express();

app.use('/graphql', graphqlHTTP({
  schema,
  graphiql: {
    subscriptionEndpoint: 'ws://localhost:4000/graphql'
  }
}));

const httpServer = http.createServer(app);

SubscriptionServer.create(
  {
    execute,
    subscribe,
    schema
  },
  {
    server: httpServer,
    path: '/graphql'
  }
);

httpServer.listen(4000, () => {
  console.log(`🚀 Server ready at http://localhost:4000/graphql`);
});