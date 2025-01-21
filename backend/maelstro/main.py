"""
Main backend app setup
"""

from typing import Annotated
from fastapi import FastAPI, Request, Response, Header


app = FastAPI(root_path="/maelstro-backend")

app.state.health_countdown = 5


@app.head("/")
@app.get("/")
def root_page():
    """
    Hello world dummy route
    """
    return {"Hello": "World"}


@app.get("/user")
def user_page(
    sec_username: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_org: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_roles: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_external_authentication: Annotated[
        str | None, Header(include_in_schema=False)
    ] = None,
    sec_proxy: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_orgname: Annotated[str | None, Header(include_in_schema=False)] = None,
):
    """
    Display user information provided by gateway
    """
    return {
        "username": sec_username,
        "org": sec_org,
        "roles": sec_roles,
        "external-authentication": sec_external_authentication,
        "proxy": sec_proxy,
        "orgname": sec_orgname,
    }


# pylint: disable=fixme
# TODO: deactivate for prod
@app.head("/debug")
@app.get("/debug")
@app.put("/debug")
@app.post("/debug")
@app.delete("/debug")
@app.options("/debug")
@app.patch("/debug")
def debug_page(request: Request):
    """
    Display details of query including headers.
    This may be useful in development to check all the headers provided by the gateway.
    This entrypoint should be deactivated in prod.
    """
    return {
        **{
            k: request[k]
            for k in [
                "type",
                "asgi",
                "http_version",
                "server",
                "client",
                "scheme",
                "root_path",
            ]
        },
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
        "query_params": request.query_params.multi_items(),
    }


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
