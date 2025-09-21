FROM node:slim
WORKDIR /app
COPY front/package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]