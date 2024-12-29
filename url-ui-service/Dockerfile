# Use the official Node.js image as a base image
FROM node:18-alpine

# Set working directory inside container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Build the React app for production
RUN npm run build

# Expose the port your app will run on
EXPOSE 3000

# Serve the app using a simple static file server (e.g., serve)
RUN npm install -g serve

# Run the app
CMD ["serve", "-s", "dist", "-l", "3000"]
