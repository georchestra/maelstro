"""
Main backend app setup
"""

# from typing import Annotated

from io import BytesIO
from fastapi import FastAPI, Response  # , Depends

# from fastapi.security import HTTPBasic, HTTPBasicCredentials

from maelstro.gn_session import GNSession


app = FastAPI(root_path="/maelstrob")
# security = HTTPBasic()

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
# def get_record_ids(credentials: Annotated[HTTPBasicCredentials, Depends(security)], server="http://gateway:8080/geonetwork/srv/api/"):
def get_record_ids(
    credentials_username: str = "testadmin",
    credentials_password: str = "testadmin",
    server="http://gateway:8080/geonetwork/srv/api/",
):
    gnSession = GNSession(server, credentials_username, credentials_password)
    return gnSession.getRecordIds()


@app.put("/record/{uuid}")
# def put_record(uuid: str, credentials: Annotated[HTTPBasicCredentials, Depends(security)], source_server: str, target_server="http://gateway:8080/geonetwork/srv/api/", overwrite=True):
def put_record(
    uuid: str,
    source_server: str,
    src_cred="admin",
    target_server="http://gateway:8080/geonetwork/srv/api",
    tgt_cred="testadmin",
    overwrite: bool = True,
):
    srcSession = GNSession(source_server, src_cred, src_cred)
    zipfile_contents = srcSession.getRecordZip(uuid)
    print(len(zipfile_contents))
    tgtSession = GNSession(target_server, tgt_cred, tgt_cred)
    r = tgtSession.uploadRecordZip(BytesIO(zipfile_contents), overwrite)
    print(type(overwrite))
    print(overwrite)
    return r.json()
