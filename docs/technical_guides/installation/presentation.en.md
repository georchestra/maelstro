# Architecture

Maelstro consists of a Vue.js single-page frontend and a Python/FastAPI backend.
The backend connects to configured GeoNetwork and GeoServer source and
destination instances. PostgreSQL can be configured to store synchronization
logs.

Use the standalone Compose file for a separate deployment, or the geOrchestra
Compose setup to integrate with a geOrchestra environment.
