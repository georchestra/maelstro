from geoutils import geOrchestra

username = 'testadmin'
password = 'testadmin'

server = "http://proxy:8080"

geOrchestra_api = geOrchestra(server, username, password)

print(geOrchestra_api.console.createnewroles(cn="MAELSTRO"))
print(geOrchestra_api.console.updaterolesuser(uuid="testadmin",cn="MAELSTRO"))
print(
    geOrchestra_api.console.createnewuser(
        org="PSC",
        sn="MAELSTRO",
        givenname="Test",
        mail="psc+maelstrotest@georchestra.org",
        description="This user is for development test of maelstro",
    )
)
