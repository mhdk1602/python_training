const { ApolloServer } = require('apollo-server');
const { PubSub } = require('graphql-subscriptions');

const typeDefs = require('./schema');
const resolvers = require('./resolvers');

const pubsub = new PubSub();

const server = new ApolloServer({ typeDefs, resolvers, context: { pubsub } });

server.listen().then(({ url, subscriptionsUrl }) => {
  console.log(`🚀  Server ready at ${url}`);
  console.log(`🚀  Subscriptions ready at ${subscriptionsUrl}`);
});