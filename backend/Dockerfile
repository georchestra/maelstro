FROM python:3.12-slim-bullseye AS poetry

RUN pip install poetry

RUN mkdir /app
WORKDIR /app

COPY pyproject.toml /app

FROM poetry as server
RUN poetry install --no-root

COPY . /app

RUN poetry install

CMD ["poetry", "run", "fastapi", "dev", "--host", "0.0.0.0", "main.py"]

FROM server as check

RUN poetry install --no-root --with check

CMD ["/app/maelstro/scripts/code_check.sh"]
