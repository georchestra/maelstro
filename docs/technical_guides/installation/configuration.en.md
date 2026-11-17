# Configuration

The server reads the YAML file specified by `MAELSTRO_CONFIG`. The supplied
Compose files mount `config/` and use `/etc/maelstro/config.yaml`; edit
[`config/config.yaml`](../../../config/config.yaml) for your deployment.

The file defines GeoNetwork and GeoServer sources, named destinations, optional
XSL transformations, and optional PostgreSQL logging. Server credentials can
be supplied as environment-variable references such as `"${SERVER_PASSWORD}"`.
Keep real credentials out of version control.

For field details and a sample, see the project
[README](../../../README.md) and [`backend/tests/test_config.yaml`](../../../backend/tests/test_config.yaml).
