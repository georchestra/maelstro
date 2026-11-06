# Troubleshooting and logs

- Check that the backend is responding at `/maelstro-backend/health`.
- Open `/maelstro-backend/docs` for the interactive FastAPI API reference.
- Inspect the backend container logs with `docker compose logs maelstro-back`.
- Check the configured source/destination URLs and credentials in the YAML
  configuration.

Synchronization history is stored in PostgreSQL when `db_logging` is
configured. The `/logs` API returns an error when database logging is not set
up.
