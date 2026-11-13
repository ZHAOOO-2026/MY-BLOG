ARG BASE_REGISTRY=docker.m.daocloud.io/library
FROM ${BASE_REGISTRY}/node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM ${BASE_REGISTRY}/nginx:stable-alpine
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
