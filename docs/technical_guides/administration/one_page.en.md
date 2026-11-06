# Deployment checklist

- Configure source and destination URLs and credentials.
- Ensure required workspaces and datastores exist on destination GeoServer
  instances.
- Configure PostgreSQL if synchronization history is required.
- For geOrchestra, configure the gateway and grant the `MAELSTRO` role as
  described in [`config/HOWTO.md`](../../../config/HOWTO.md).