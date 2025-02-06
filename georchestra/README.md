## Prepare geOrchestra

Refer to documentation from https://github.com/georchestra/docker/tree/master?tab=readme-ov-file#on-linux to trust caddy certificate.

Following commands should be runned from repository root folder.

```bash
# Prepare geOrchestra config
git submodule update --init --recursive
cd georchestra/config
git apply ../0001-tweat-gateway-and-security-proxy-config-to-host-mael.patch
cd ../../
docker compose up -d

# Add role MAELSTRO + add testadmin into it, + create tmaelstro
docker compose run --rm \
    -v $(pwd)/georchestra:/georchestra \
    check \
    python3 /georchestra/init-plateform.py

# Set user tmaelstro password to tmaelstro
docker compose exec -it ldap bash -c "ldapmodify -H ldap://localhost:389 -D cn=admin,dc=georchestra,dc=org -w secret  << EOF
dn: uid=tmaelstro,ou=users,dc=georchestra,dc=org
changetype: modify
add: userPassword
userPassword:: e1NTSEF9cXlQT25BQUkzei9lb3JEZ0FDa3JzYy9hcmRjcGpCdVNyTDBya3c9PQ=
 =


EOF"

# Create required GeoServer workspace and datastore
docker compose run --rm \
    -v $(pwd)/georchestra/create_maelstro_gs_rsc.py:/scripts/create_maelstro_gs_rsc.py \
    check \
    python3 /scripts/create_maelstro_gs_rsc.py

# Insert required dataset in PostGIS
docker compose cp georchestra/psc_antenne.sql postgis:/psc_antenne.sql
docker compose exec postgis bash -c "psql -U georchestra -d datafeeder < psc_antenne.sql"
```
