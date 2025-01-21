FROM python:3.12-slim-bullseye AS poetry

RUN  --mount=type=cache,target=/root/.cache \
     pip install poetry
RUN poetry config virtualenvs.create false

RUN mkdir /app
WORKDIR /app

COPY pyproject.toml /app

FROM poetry as server
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root

COPY . /app

RUN --mount=type=cache,target=/root/.cache \
    poetry install

CMD ["serve_prod"]

FROM server as check

RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --with check

CMD ["/app/maelstro/scripts/code_check.sh"]
