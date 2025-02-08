# Use an official Node.js runtime as a parent image

FROM ubuntu:20.04

# 安装 Node.js 和 npm
RUN apt-get update && apt-get install -y nodejs npm


# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port that the app will run on
EXPOSE 8080


CMD pip install flask
# Define the command to run your app
CMD npm run dev & python run-data-backend.py
