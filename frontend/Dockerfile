FROM node:20-alpine
WORKDIR /workspace/frontend

COPY package.json ./

RUN npm install

COPY . .

#EXPOSE 5173