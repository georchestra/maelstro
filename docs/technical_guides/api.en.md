# API

The interactive API reference is available at
`/maelstro-backend/docs` on a running deployment.

| Endpoint | Purpose |
|---|---|
| `GET /sources` | List configured GeoNetwork sources |
| `GET /destinations` | List configured destination platforms |
| `GET /transformations` | List configured XSL transformations |
| `POST /search/{src_name}` | Search a source catalog |
| `GET /copy_preview` | Preview a dataset copy |
| `PUT /copy` | Copy selected metadata, layers, and styles |
| `GET /logs` | Retrieve synchronization history |
| `GET /health` | Check backend availability |


# Development

The frontend is in `frontend/` (Vue.js, Vite, TypeScript); the backend is in
`backend/` (Python, FastAPI). The backend API is documented by FastAPI's
interactive interface at `/maelstro-backend/docs`.

- [API overview](api.md)
- [Feature summary](feature_matrix.md)

The root [README](../../../README.md) includes local development and test
commands.
