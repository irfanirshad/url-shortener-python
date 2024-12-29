# Use a base image with Node.js (adjust version as needed)
FROM node:16

# Set working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all the frontend source code
COPY . .

# Build the frontend (if using build step like with React, Vue, etc.)
RUN npm run build

# Expose port for the frontend application
EXPOSE 80

# Start the frontend app
CMD ["npm", "start"]
