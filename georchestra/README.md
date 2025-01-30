# Maelstro docker composition

accessible from https://georchestra-127-0-0-1.nip.io/maelstro-backend/

testadmin:testadmin
tmaelstro:tmaelstro

Start composition

```
# from root
git submodule update --init --recursive
cd georchestra/config
git apply ../0001-tweat-gateway-and-security-proxy-config-to-host-mael.patch
cd ../../
docker compose up -d

# add role MAELSTRO + add testadmin into it, + create tmaelstro
python3 georchestra/init-plateform.py
# set user tmaelstro password to tmaelstro
docker compose exec -it ldap bash -c "ldapmodify -H ldap://localhost:389 -D cn=admin,dc=georchestra,dc=org -w secret  << EOF
dn: uid=tmaelstro,ou=users,dc=georchestra,dc=org
changetype: modify
add: userPassword
userPassword:: e1NTSEF9cXlQT25BQUkzei9lb3JEZ0FDa3JzYy9hcmRjcGpCdVNyTDBya3c9PQ=
 =


EOF"

# init GS
pip install geoservercloud --user
python3 georchestra/create_maelstro_gs_rsc.py

# init geoserver database data
docker compose cp georchestra/psc_antenne.sql postgis:/psc_antenne.sql
docker compose exec -it postgis bash -c "psql -U georchestra -d datafeeder < psc_antenne.sql"


```

