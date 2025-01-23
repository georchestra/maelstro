FROM python:3.12-slim-bullseye AS poetry

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

FROM poetry as server
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root

COPY . /app
RUN chown -R appuser:appgroup /app

RUN --mount=type=cache,target=/root/.cache \
    poetry install

RUN chown -R appuser:appgroup /app

USER appuser

CMD ["serve_prod"]

FROM server as check

RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --with check

CMD ["/app/maelstro/scripts/code_check.sh"]
