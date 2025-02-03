from geoservercloud import GeoServerCloud
import csv

# https://github.com/camptocamp/python-geoservercloud

cat = GeoServerCloud(url="http://proxy:8080/geoserver",
                     user="testadmin",
                     password="testadmin")

ws='psc'
ds="datafeeder_psc"

try:
    cat.create_workspace(ws)
except:
    print("pb with workspace")
try:
    cat.create_jndi_datastore(ws,
                              ds,
                              "jdbc/datafeeder",
                              "psc",
                              "Datafeeder uploaded datasets")
except:
    print("Error creating the datastore")
    pass
