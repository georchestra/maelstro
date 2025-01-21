# maelstro
geOrchestra Maelstro is an application which helps synchronise geonetwork and geoserver instances


## run it in docker
Refer to documentation from https://github.com/georchestra/docker/tree/master?tab=readme-ov-file#on-linux to trust caddy certificate

Also you need to run few commands before to start documented here : [georchestra/README.md](georchestra/README.md)
 
## Backend
 
The folder [backend](backend) contains the API written with FastAPI.
 
### Access

In the global dev composition, the backend is accessible via the https gateway:
https://georchestra-127-0-0-1.nip.io/maelstro-backend/

### SwaggerUI

FastAPI automatically builds a swagger API web interface which can be found at
https://georchestra-127-0-0-1.nip.io/maelstrob/docs

Here the various API entrypoints can be tested

## CI

Automatic code quality checks are implemented in the CI.

The code test can be launched manually via the docker command below.
```
docker compose run --rm  check
```

In case formatting issues are found, the code can be auto-fixed with:
```
docker compose run --rm  check /app/maelstro/scripts/code_fix.sh
```
