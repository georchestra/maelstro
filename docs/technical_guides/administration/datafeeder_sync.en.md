# Synchronizing Datafeeder datasets

Maelstro can synchronize a dataset managed by Datafeeder in addition to its
GeoNetwork metadata. The feature identifies the Datafeeder dataset by using the
UUID of the metadata selected in the synchronization form.

## Configuration

Configure Datafeeder next to the existing GeoNetwork and GeoServer services.
The Datafeeder source name must match the corresponding GeoNetwork source name.

```yaml
sources:
  geonetwork_instances:
    - name: sourcePlatform
      api_url: "${SOURCE_GEONETWORK_URL}"
  geoserver_instances:
    - url: "${SOURCE_GEOSERVER_URL}"
  datafeeder_instances:
    - name: sourcePlatform
      url: "${SOURCE_DATAFEEDER_URL}"
      login: "${SOURCE_LOGIN}"
      password: "${SOURCE_PASSWORD}"

destinations:
  destinationPlatform:
    geonetwork:
      api_url: "${DESTINATION_GEONETWORK_URL}"
    geoserver:
      url: "${DESTINATION_GEOSERVER_URL}"
    datafeeder:
      url: "${DESTINATION_DATAFEEDER_URL}"
      login: "${DESTINATION_LOGIN}"
      password: "${DESTINATION_PASSWORD}"
```

The `url`, `api_url`, `login` and `password` values can be resolved from
environment variables. Credentials should not be committed to the repository.

## Form behavior

The **Import with Datafeeder** toggle controls the `copy_data` option sent to
the backend.

- The toggle is shown only when the selected source has a matching entry in
  `datafeeder_instances`.
- Selecting another source dataset clears the previous Datafeeder result and
  disables `copy_data`.
- While availability is being checked, the toggle is disabled.
- The toggle remains disabled when the selected metadata UUID is not found in
  Datafeeder.
- Enabling the toggle forces **Metadata**, **Layers** and **Styles** on and
  disables all three toggles because every synchronization option is mandatory
  for a Datafeeder import.
- Disabling Datafeeder makes all three synchronization options editable again;
  they keep their current values.

The source configuration returned by the backend controls the toggle visibility.
When a dataset is selected, the frontend asks Maelstro to query the configured
source Datafeeder by metadata UUID. The result controls the availability message
and whether the toggle can be enabled.

## Preview

Pressing **Synchronize** only builds a preview; it does not modify the
destination. When `copy_data` is enabled, the preview queries the source and
destination Datafeeder admin endpoints and shows:

- whether the source dataset was found;
- the integrity-link identifier;
- the source import type;
- the final table name;
- whether the table exists on the destination;
- the dataset currently using that table, if any;
- the planned action.

Possible actions are:

| Action | Meaning |
| --- | --- |
| `no_dataset` | The metadata UUID is not registered in the source Datafeeder. |
| `no_table` | The import type does not require a table, or no final table is defined. |
| `copy_table` | The table must be streamed to the destination. |
| `reuse_table` | The table already exists and is not attached to another dataset. |
| `conflict` | The table is already used by another dataset; the copy is rejected. |
| `already_imported` | The metadata UUID already has an integrity link on the destination. |

## Confirmed synchronization

Pressing **Confirm** performs the write operations. With the default toggle
state, Maelstro keeps this order:

1. Copy the metadata record to the destination GeoNetwork.
2. Reuse the destination table or stream it from the source Datafeeder.
3. Call the destination Datafeeder import endpoint with
   `copy_recurrence: true`.

Table contents are streamed in chunks through Maelstro and are not loaded
entirely into memory. The upload uses an extended timeout because Datafeeder
answers after loading and indexing the table.

The operation is resumable:

- an existing free table is reused;
- an already imported metadata UUID is not imported again;
- a table owned by another dataset produces a conflict instead of being
  overwritten.

For Datafeeder-managed datasets, layers and styles are off by default because
the destination import is responsible for attaching the resulting resources.
If the user manually enables either toggle, Maelstro also runs the existing
GeoServer layer/style copy behavior.

## Operation logs

Datafeeder HTTP calls and results are recorded with the `Datafeeder` operation
context. The confirmation screen displays these records together with metadata,
layer and style operations.

## Current scope

This implementation supports direct table transfer and table reuse.
**Reprocess from source** is intentionally not implemented. A future version
may use that option to ask the destination Datafeeder to run the original
database, API, URL or FTP ingestion again instead of transferring a large
table through Maelstro.

The Datafeeder admin endpoints used by this workflow are internal APIs. Source
and destination deployments must provide compatible endpoint versions.
