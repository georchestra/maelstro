# Run Maelstro

For a standalone deployment, select the Compose file and start the services:

```sh
ln -s docker-compose-solo.yml docker-compose.yml
docker compose up -d
```

Open [http://127.0.0.1:8080/maelstro/](http://127.0.0.1:8080/maelstro/).
To use geOrchestra, follow the setup in [`config/HOWTO.md`](../../../config/HOWTO.md)
and the geOrchestra section of the [project README](../../../README.md).
