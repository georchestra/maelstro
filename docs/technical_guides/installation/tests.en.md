# Health checks and tests

The backend health endpoint is `/maelstro-backend/health`. For local tests and
quality checks, the project README documents the Docker commands used by CI:

```sh
docker compose -f docker-compose-dev.yml run --rm check pytest --cov=maelstro tests/
```

The frontend also has unit tests (`npm run test:unit` from `frontend/`).
