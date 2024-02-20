# Use the official Node.js image
FROM node:14

# Create a directory for the app
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the local files to the container
COPY . .

# Expose the port the app runs on
EXPOSE 4000

# Define the command to run the app
CMD [ "node", "server.js" ]