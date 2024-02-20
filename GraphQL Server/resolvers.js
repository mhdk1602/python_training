let messages = [];
let idCount = 0;

const resolvers = {
  Query: {
    messages: () => messages,
  },
  Mutation: {
    addMessage: (_, { user, content }) => {
      const message = { id: idCount++, user, content };
      messages.push(message);
      pubsub.publish('MESSAGE_ADDED', { messageAdded: message });
      return message;
    },
  },
  Subscription: {
    messageAdded: {
      subscribe: (_, __, { pubsub }) => pubsub.asyncIterator(['MESSAGE_ADDED']),
    },
  },
};

module.exports = resolvers;