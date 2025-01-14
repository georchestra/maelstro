"""
Main backend app setup
"""

from fastapi import FastAPI, Response


app = FastAPI()

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
