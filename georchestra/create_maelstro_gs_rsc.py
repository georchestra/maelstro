from geoservercloud import GeoServerCloud
import csv

# https://github.com/camptocamp/python-geoservercloud

cat = GeoServerCloud(url="https://georchestra-127-0-0-1.nip.io/geoserver",
                     user="testadmin",
                     password="testadmin")

ws='psc'
ds="datafeeder_psc"

try:
    cat.create_workspace(workspace=ws)
except:
    print("pb with workspace")
try:
    cat.create_jndi_datastore(workspace=ws,
                              datastore=ds,
                              jndi_reference="jdbc/datafeeder",
                              schema="psc",
                              description="Datafeeder uploaded datasets")
except:
    print("Error creating the datastore")
    pass
