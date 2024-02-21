const users = [
    { id: '1', name: 'Alice', age: 30 },
    { id: '2', name: 'Bob', age: 40 },
    { id: '3', name: 'Charlie', age: 25 }
  ];
  
  function getUserById(userId) {
    return users.find(user => user.id === userId);
  }
  
  module.exports = { getUserById };  