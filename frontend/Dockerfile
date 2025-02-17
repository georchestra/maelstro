# Inspired from https://cli.vuejs.org/guide/deployment.html#docker-nginx

FROM node:22 AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm install

COPY ./ .
RUN npm run build


FROM nginxinc/nginx-unprivileged:1.27-alpine

ENV CUSTOM_SCRIPTS_DIRECTORY ""
COPY --from=builder --chown=nginx /app/dist /app
COPY nginx-default.conf.template /etc/nginx/templates/nginx-default.conf.template
COPY ./docker-entrypoint.sh /
