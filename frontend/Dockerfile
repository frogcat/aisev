FROM node:24-slim

WORKDIR /app
COPY ./app .

ENV no_proxy 0.0.0.0, localhost
RUN npm install

EXPOSE 5173




