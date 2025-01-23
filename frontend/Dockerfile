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

## add permissions
RUN chown -R nginx:nginx /app && chmod -R 755 /app && \
        chown -R nginx:nginx /var/cache/nginx && \
        chown -R nginx:nginx /var/log/nginx && \
        chown -R nginx:nginx /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && \
        chown -R nginx:nginx /var/run/nginx.pid

## switch to non-root user
USER nginx