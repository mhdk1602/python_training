const { getUserById } = require('./data');
const { pubsub } = require('./pubsub');

let transactions = [];
let idCount = 0;

const resolvers = {
  Query: {
    transactions: () => transactions,
  },
  Mutation: {
    addTransaction: (_, { userId, amount }) => {
      const user = getUserById(userId);
      const transaction = { id: idCount++, userId, amount, user };
      transactions.push(transaction);
      pubsub.publish('TRANSACTION_ADDED', { transactionAdded: transaction });
      return transaction;
    },
  },
  Subscription: {
    transactionAdded: {
      subscribe: () => pubsub.asyncIterator(['TRANSACTION_ADDED']),
    },
  },
};

module.exports = resolvers;