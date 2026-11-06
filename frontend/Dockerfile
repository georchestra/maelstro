# Inspired from https://cli.vuejs.org/guide/deployment.html#docker-nginx

FROM node:22 AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm install

COPY ./ .
RUN npm run build


FROM nginxinc/nginx-unprivileged:1.29-alpine

ENV CUSTOM_SCRIPTS_DIRECTORY ""
COPY --from=builder --chown=nginx /app/dist /app
COPY nginx-default.conf.template /etc/nginx/templates/default.conf.template
COPY ./docker-entrypoint.sh /

# OCI image labels (https://github.com/opencontainers/image-spec/blob/main/annotations.md)
LABEL org.opencontainers.image.title="Maelstro frontend"
LABEL org.opencontainers.image.description="Maelstro frontend module for the geOrchestra SDI"
LABEL org.opencontainers.image.authors="geOrchestra"
LABEL org.opencontainers.image.vendor="geOrchestra"
LABEL org.opencontainers.image.licenses="GPL-3.0-or-later"
LABEL org.opencontainers.image.url="https://github.com/georchestra/maelstro"
LABEL org.opencontainers.image.documentation="https://docs.georchestra.org/"
LABEL org.opencontainers.image.source="https://github.com/georchestra/maelstro"
