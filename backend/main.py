from fastapi import FastAPI, Response

app = FastAPI()

app.state.health_countdown = 5

@app.get("/")
def root_page():
    return {"Hello": "World"}


@app.get("/health")
def health_check(response: Response):
    status: str = "healthy"
    if app.state.health_countdown > 0:
        app.state.health_countdown -= 1
        response.status_code = 404
        status = "unhealthy"
    return {"status": status, "user": None}
