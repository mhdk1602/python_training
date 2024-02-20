const { gql } = require('apollo-server');

const typeDefs = gql`
  type Message {
    id: ID!
    user: String!
    content: String!
  }

  type Subscription {
    messageAdded: Message
  }

  type Query {
    messages: [Message]
  }

  type Mutation {
    addMessage(user: String!, content: String!): Message
  }
`;

module.exports = typeDefs;