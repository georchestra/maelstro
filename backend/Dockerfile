FROM python:3.13-slim-trixie AS poetry

# set fixed UID and GID - see github.com/hexops/dockerfile
ARG UID=10000
ARG GID=10001

RUN addgroup --gid ${GID} appgroup
RUN adduser --uid ${UID} --disabled-password --home /app --shell /bin/sh --ingroup appgroup appuser

RUN  --mount=type=cache,target=/root/.cache \
     pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app

COPY pyproject.toml /app

FROM poetry AS server
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root

COPY . /app
RUN chown -R appuser:appgroup /app

RUN --mount=type=cache,target=/root/.cache \
    poetry install

RUN chown -R appuser:appgroup /app

USER appuser

# OCI image labels (https://github.com/opencontainers/image-spec/blob/main/annotations.md)
LABEL org.opencontainers.image.title="Maelstro backend"
LABEL org.opencontainers.image.description="Maelstro backend module for the geOrchestra SDI"
LABEL org.opencontainers.image.authors="geOrchestra"
LABEL org.opencontainers.image.vendor="geOrchestra"
LABEL org.opencontainers.image.licenses="GPL-3.0-or-later"
LABEL org.opencontainers.image.url="https://github.com/georchestra/maelstro"
LABEL org.opencontainers.image.documentation="https://docs.georchestra.org/"
LABEL org.opencontainers.image.source="https://github.com/georchestra/maelstro"

CMD ["serve_prod"]

FROM server AS check
USER root
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --with check

CMD ["/app/maelstro/scripts/code_check.sh"]
