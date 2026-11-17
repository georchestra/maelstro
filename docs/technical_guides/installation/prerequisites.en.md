## Prerequisites

- Configure User/password for all plateforme (read and write), this user need to have the role **ADMINISTRATOR** and **GN_EDITOR**
- Configure source and destination URLs and credentials.
- Ensure required workspaces and datastores exist on destination GeoServer
  instances.
- Configure PostgreSQL if synchronization history is required.
- For geOrchestra, configure the gateway and grant the `MAELSTRO` role as
  described in [`config/HOWTO.md`](../../../config/HOWTO.md).


Maelstro has no separate data-management console. Administrators maintain the
server-side YAML configuration, ensure destination GeoServer workspaces and
datastores exist, and manage access through their deployment's authentication
system.

For geOrchestra roles, proxy routes, and header setup, see
[`config/HOWTO.md`](../../../config/HOWTO.md).
