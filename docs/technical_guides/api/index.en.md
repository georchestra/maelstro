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
