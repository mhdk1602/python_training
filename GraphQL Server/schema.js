const { gql } = require('apollo-server');

const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    age: Int!
  }

  type Transaction {
    id: ID!
    userId: ID!
    amount: Float!
    user: User!
  }

  type Subscription {
    transactionAdded: Transaction
  }

  type Query {
    transactions: [Transaction]
  }

  type Mutation {
    addTransaction(userId: ID!, amount: Float!): Transaction
  }
`;

module.exports = typeDefs;