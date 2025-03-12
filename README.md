# Maelstro

geOrchestra Maelstro is an application which helps synchronise geonetwork and geoserver instances

## Docker deploy

### Solo quick start (without included geOrchestra composition)

Maelstro can be used outside geOrchestra.

First select the `docker-compose-solo.yml` file as current composition:

```bash
ln -s docker-compose-solo.yml docker-compose.yml
```

Then start the compositon:

```bash
docker compose up
```

Open : http://127.0.0.1:8080/maelstro/
There is no authentication to access the page but if needed it can be done with basic auth in the [nginx config](./config/nginx-solo.conf) (or another way)

### Quick start with geOrchestra

First select the `docker-compose-geOrchestra.yml` file as current composition:

```bash
ln -s docker-compose-geOrchestra.yml docker-compose.yml
```

Before starting development you need to setup some geOrchestra configurations.

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

### Development

For development purpose, you may need to use `docker-compose-dev.yml` instead:

```bash
rm -f docker-compose.yml
ln -s docker-compose-dev.yml docker-compose.yml
```

And maybe add overrides for debugging:

```bash
cp docker-compose.override.sampl.yml docker-compose.override.yml
```

## Kubernetes deployment

The [helm](helm/) folder contains a helm chart which can be used to deploy the app.

## Frontend development

The folder [frontend](frontend) contains the SPA written with VueJS.

Refer to documentation in [frontend/README.md](frontend/README.md)

## Backend

The folder [backend](backend) contains the API written with FastAPI.

### Configuration

The configuration is based on a YAML file containing connection information about the source and destination servers. You can find an example of this file in [test_config.yaml](backend/tests/test_config.yaml)

For dev use of the platform, there is a sample config in the backend folder: [dev_config.yaml](backend/dev_config.yaml). This config is used by default in the docker compo.

The file has 4 distict parts:

- sources
- destinations
- db_logging
- transformations

#### Sources

`Sources` contains 2 list of servers: `geonetwork_instances` and `geoserver_instances`. Each instance is described by its `url` (`api_url` for geonetwork), and their credentials.

#### Destinations

`Destinations` is a dict of geonetwork / geoserver combinations, each with their `url` and credentials.

#### DB logging

The section db_logging contains all connection information to reach a writable postgres DB to use for writing and reading operation logs:

- host (default: database)
- port (default: 5432)
- login (default: georchestra)
- password (default: georchestra)
- database (default: georchestra)
- schema (default: maelstro
- table: (default: logs)

Substitution of credentials (login and password) can be done for the DB configuration the same way as for server credentials (see below)

#### Transformations

The `transformations` section conatains a list of xsl transformations which can be applied to the xml metadata of source or destination servers.

Each named `transformation` item must conatain

- `xslt_path`: local path on the server to an xsl file in which the trasformation is defind (typically in the datadir)
- `description`: Details of the transformation content to easily identify which transformation is applied

For each geonetwork item of the source and destination servers, a specific key is added to the configuration file:

- transformations: list of xslt keys to be applied to the metadata of the corresponding geonetwork server

If a list of transformations is defined for both the source and destination server, the copy operation is executed in the way described below:

- read metadata from source
- apply all source transformations
- apply all destination transformations
- write metadata to destination server

for an example of a transformation chain source -> destination, you can refer to the configuration https://github.com/georchestra/maelstro/blob/main/backend/tests/test_xslt_config.yaml used in the test: https://github.com/georchestra/maelstro/blob/main/backend/tests/test_meta.py#L76

#### Credentials

All credentials (for source, destination or DB server) can be read from an ENV var or can be hard-coded into the conf file

The logics for credentials is by decreasing order of importance:

1. env var: automatic detection with regex, if match "${..}" (classic usage of env var) it will try to resolve it
2. if no env vars can be found for the key, the keys "login" and/or password are read literrally from the config file
3. if still no login/password is found, the configuration file is parsed at the parent hierarchy level. First env vars are used like in 1.
4. Then constant login/password keys are read
5. If still either "login" or "password" is not defined, the credentials are considered invalid and anonymous acces is used for the instance without authentication

#### Example

(see [doc_sample_config.yaml](backend/tests/doc_sample_config.yaml)):

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
docker compose -f docker-compose-dev.yml run --rm  check
```

In case formatting issues are found, the code can be auto-fixed with:

```bash
docker compose -f docker-compose-ci.yml run --rm  check /app/maelstro/scripts/code_fix.sh
```

To launch the tests locally, use the command as in github CI:

```bash
docker compose -f docker-compose-ci.yml run --rm  check pytest --cov=maelstro tests/
```

or

```bash
docker compose -f docker-compose-ci.yml run --rm  check pytest --cov=maelstro --cov-report=html tests/
```
