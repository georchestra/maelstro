Maelstro provides two main views:

- **Synchronization**: search the configured source catalog, choose a
  destination and copy options, then preview and run a copy.
- **Logs**: browse previous synchronization runs, page through results, and
  expand a run to inspect its operations.

## Synchronization options

The synchronization form lets you:

- Search the configured GeoNetwork source, optionally including harvested
  datasets.
- Select a configured destination.
- Independently include or exclude metadata, linked GeoServer layers, and their
  styles.

Submit the form to preview the resources and operations before confirming the
copy. The available options depend on the dataset and configured servers.

## Start synchronize

1. Open Maelstro and select a source dataset using the search field. Use **Include
   harvested datasets** if you also want to search harvested records.
2. Select a destination platform.
3. Choose whether to copy the metadata, linked layers, and styles.
4. Submit the form to review the copy preview, then confirm to run the
   synchronization.
5. Review the operation results. Previous runs are available in the logs view.

The source catalog and destination list are provided by the server configuration;
they cannot be changed from the form.
