from geoservercloud import GeoServerCloud

# https://github.com/camptocamp/python-geoservercloud

cat = GeoServerCloud(
    url="http://proxy:8080/geoserver",
    user="testadmin",
    password="testadmin",
)

ws='psc'
ds="datafeeder_psc"

cat.create_workspace(ws)

cat.create_jndi_datastore(
    workspace_name=ws,
    datastore_name=ds,
    jndi_reference="jdbc/datafeeder",
    pg_schema="psc",
    description="Datafeeder uploaded datasets",
)
