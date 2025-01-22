# Inspired from https://cli.vuejs.org/guide/deployment.html#docker-nginx

FROM node:22 AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm install

COPY ./ .
RUN npm run build


FROM nginx:1.27-alpine AS server

RUN mkdir /app
ENV CUSTOM_SCRIPTS_DIRECTORY ""
COPY --from=builder /app/dist /app
COPY nginx.conf /etc/nginx/nginx.conf
COPY ./docker-entrypoint.sh /
