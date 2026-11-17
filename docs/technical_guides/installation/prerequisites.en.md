# Prerequisites

For a Docker Compose deployment, install Docker Engine with the Compose plugin.
The deployment must be able to reach the configured GeoNetwork and GeoServer
instances.

For local development, use Python 3.12 or newer for the backend and Node.js
matching the version in `frontend/.nvmrc` for the frontend.


# Administration

Maelstro has no separate data-management console. Administrators maintain the
server-side YAML configuration, ensure destination GeoServer workspaces and
datastores exist, and manage access through their deployment's authentication
system.

For geOrchestra roles, proxy routes, and header setup, see
[`config/HOWTO.md`](../../../config/HOWTO.md).

# Deployment checklist

- Configure source and destination URLs and credentials.
- Ensure required workspaces and datastores exist on destination GeoServer
  instances.
- Configure PostgreSQL if synchronization history is required.
- For geOrchestra, configure the gateway and grant the `MAELSTRO` role as
  described in [`config/HOWTO.md`](../../../config/HOWTO.md).
