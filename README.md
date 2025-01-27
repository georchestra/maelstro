# maelstro
geOrchestra Maelstro is an application which helps synchronise geonetwork and geoserver instances


## run it in docker
Refer to documentation from https://github.com/georchestra/docker/tree/master?tab=readme-ov-file#on-linux to trust caddy certificate

Also you need to run few commands before to start documented here : [georchestra/README.md](georchestra/README.md)

## Frontend

The folder [frontend](frontend) contains the SPA written with VueJS.

### Access

In the global dev composition, the backend is accessible via the https gateway:
https://georchestra-127-0-0-1.nip.io/maelstro/

### Development

Refer to documentation in [frontend/README.md](frontend/README.md)

## Backend
 
The folder [backend](backend) contains the API written with FastAPI.

### Configuration

The configuration is based on a YAML file containing connection information about the source and destination servers. You can find an example of this file in <backend/tests/test_config.yaml>

The file has 2 categories:
- sources
- destinations

Sources contains 2 list of servers: `geonetwork_instances` and `geoserver_instances`. Each instance is described bu its url (api_url for geonetwork), and their credentials.

Destinations is a dict of geonetwork / geoserver combinations, each with their url and credentials.

The logics for credentials is by increasing order of importance:
- credentials defined at a higher level are applied to a lower level (e.g. common credentials can be defined for both geonetwork and geoserver in a destination item)
- credentials in the geoserver/geonetwork level are read from the keys "login", "password"
- if the keys "login_env_var" and/or "password_env_var" are found, the corrensponding environment variable is read, and if defined, overrides the credential
 
### Access

In the global dev composition, the backend is accessible via the https gateway:
https://georchestra-127-0-0-1.nip.io/maelstro-backend/

### SwaggerUI

FastAPI automatically builds a swagger API web interface which can be found at
https://georchestra-127-0-0-1.nip.io/maelstro-backend/docs

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
