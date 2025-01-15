"""
Main backend app setup
"""

from io import BytesIO
from fastapi import FastAPI, Response

from maelstro.gn_session import GNSession


app = FastAPI(root_path="/maelstrob")

app.state.health_countdown = 5


@app.get("/")
def root_page():
    """
    Hello world dummy route
    """
    return {"Hello": "World"}


@app.get("/health")
def health_check(response: Response):
    """
    Health check to make sure the server is up and running
    For test purposes, the server is reported healthy only from the 5th request onwards
    """
    status: str = "healthy"
    if app.state.health_countdown > 0:
        app.state.health_countdown -= 1
        response.status_code = 404
        status = "unhealthy"
    return {"status": status, "user": None}


@app.get("/record/ids")
def get_record_ids(
    credentials_username: str = "testadmin",
    credentials_password: str = "testadmin",
    server="http://gateway:8080/geonetwork/srv/api/",
):
    gn_session = GNSession(server, credentials_username, credentials_password)
    return gn_session.get_record_ids()


@app.put("/record/{uuid}")
def put_record(
    uuid: str,
    source_server: str,
    source_username,
    source_password,
    target_server="http://gateway:8080/geonetwork/srv/api",
    target_username="testadmin",
    target_password="testadmin",
    overwrite: bool = True,
):
    """
    Entrypoint for cloning a geonetwork entry
    Currently, the credentials for the target server must be given, but eventually, these will be handled
    by the gateway via headers
    """
    src_session = GNSession(source_server, source_username, source_password)
    zipfile_contents = src_session.get_record_zip(uuid)
    tgt_session = GNSession(target_server, target_username, target_password)
    r = tgt_session.upload_record_zip(BytesIO(zipfile_contents), overwrite)
    return r.json()
