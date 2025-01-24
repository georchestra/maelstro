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

The configuration is based on a YAML file containing connection information about the source and destination servers. You can find an example of this file in [test_config.yaml](backend/tests/test_config.yaml)

The file has 2 categories:
- sources
- destinations

Sources contains 2 list of servers: `geonetwork_instances` and `geoserver_instances`. Each instance is described by its `url` (`api_url` for geonetwork), and their credentials.

Destinations is a dict of geonetwork / geoserver combinations, each with their `url` and credentials.

The logics for credentials is by decreasing order of importance:
1. env var: if the keys "login_env_var" and/or "password_env_var" are found in a single server definitions and if the corrensponding environment variable is defined, this value is read and applied as login /password
2. if no env vars are configured, the keys "login" and/or password for a single server instance are used
3. if still no login/password is found, the configuration file is parsed at the parent hierarchy level. First env vars are used like in 1.
4. Then constant login/password keys are read
5. I still either "login" or "password" is not defined, the credentials are considered invalid and anonymous acces is used for the instance without authentication

Example (see [doc_sample_config.yaml](backend/tests/doc_sample_config.yaml)):

```
sources:
  login: admin
  password_env_var: COMMON_PW
  geonetwork_instances:
  - name: "a"
    password: "pwA"
  - name: "b"
    login: "B"
    password: default_unused
    password_env_var: "PASSWORD_B"
  - name: "c"
    login: "C"
```
where `COMMON_PW`is undefined and `PASSWORD_B=pwB`

in this case, the parsed credentials will be:
- instance a: login: admin, password: pwA
- instance b: login: B, password: pwB
- instance c: anonymous since no password is defined
 
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

To launch the tests locally, use the command as in github CI:
```
docker compose run --rm  check pytest --cov=maelstro tests/
```
or
```
docker compose run --rm  check pytest --cov=maelstro --cov-report=html tests/
```
