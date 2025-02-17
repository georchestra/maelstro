# Maelstro

geOrchestra Maelstro is an application which helps synchronise geonetwork and geoserver instances

## Quick start with geOrchestra

Before starting developement you need to setup some geOrchestra configurations.

See commands documented here: [georchestra/README.md](georchestra/README.md)

Now you can run the Docker composition:

```bash
docker compose up -d
```

Then application should be available at:

Frontend: https://georchestra-127-0-0-1.nip.io/maelstro/
Backend: https://georchestra-127-0-0-1.nip.io/maelstro-backend/

With credentials:

- testadmin:testadmin
- tmaelstro:tmaelstro

## Solo quick start
Maelstro can be used outside geOrchestra.

```
docker compose -f docker-compose-solo.yml up 
```
Open : http://127.0.0.1:8080/maelstro/ 
There is no authentication to access the page but if needed it can be done with basic auth in the [nginx config](./config/nginx-solo.conf) (or another way)

## Frontend developement

The folder [frontend](frontend) contains the SPA written with VueJS.

Refer to documentation in [frontend/README.md](frontend/README.md)

## Backend

The folder [backend](backend) contains the API written with FastAPI.

### Configuration

The configuration is based on a YAML file containing connection information about the source and destination servers. You can find an example of this file in [test_config.yaml](backend/tests/test_config.yaml)

For dev use of the platform, there is a sample config in the backend folder: [dev_config.yaml](backend/dev_config.yaml). This config is used by default in the docker compo.

The file has 3 categories:
- sources
- destinations
- db_logging

Sources contains 2 list of servers: `geonetwork_instances` and `geoserver_instances`. Each instance is described by its `url` (`api_url` for geonetwork), and their credentials.

Destinations is a dict of geonetwork / geoserver combinations, each with their `url` and credentials.

The logics for credentials is by decreasing order of importance:

1. env var: automatic detection with regex, if match "${..}" (classic usage of env var) it will try to resolv it
2. if no env vars are configured, the keys "login" and/or password for a single server instance are used
3. if still no login/password is found, the configuration file is parsed at the parent hierarchy level. First env vars are used like in 1.
4. Then constant login/password keys are read
5. I still either "login" or "password" is not defined, the credentials are considered invalid and anonymous acces is used for the instance without authentication

The section db_logging contains all connection information to reach a writable postgres DB to use for writing and reading application logs:
- host (default: database)
- port (default: 5432)
- login (default: georchestra)
- password (default: georchestra)
- database (default: georchestra)
- schema (default: maelstro
- table: (default: logs)

Substitution of credentials (login and password) can be done for the DB configuration the same way as for server credentials (login_env_var)


Example (see [doc_sample_config.yaml](backend/tests/doc_sample_config.yaml)):

```yaml
sources:
  login: "admin"
  password: "${COMMON_PW}"
  geonetwork_instances:
    - name: "a"
      password: "pwA"
    - name: "b"
      login: "B"
      password: "${PASSWORD_B}"
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

```bash
docker compose run --rm  check
```

In case formatting issues are found, the code can be auto-fixed with:

```bash
docker compose run --rm  check /app/maelstro/scripts/code_fix.sh
```

To launch the tests locally, use the command as in github CI:

```bash
docker compose run --rm  check pytest --cov=maelstro tests/
```

or

```bash
docker compose run --rm  check pytest --cov=maelstro --cov-report=html tests/
```
