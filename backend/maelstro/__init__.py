"""
Entry point scripts for maelstro backend server
"""

import uvicorn
from fastapi_cli.utils.cli import get_uvicorn_log_config


def dev() -> None:
    """
    Dev server entrypoint:
    special configuration:
    - listens only on localhost
    - restarts on code change
    """
    uvicorn.run(
        app="maelstro.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        workers=None,
        root_path="",
        # proxy_headers=proxy_headers,
        log_config=get_uvicorn_log_config(),
    )


def docker_dev() -> None:
    """
    Dev server entrypoint for running the server inside a docker container:
    special configuration:
    - restarts on code change
    """
    uvicorn.run(
        app="maelstro.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=None,
        root_path="",
        # proxy_headers=proxy_headers,
        log_config=get_uvicorn_log_config(),
    )


def prod() -> None:
    """
    Server entrypoint for running the server inside a docker container:
    """
    uvicorn.run(
        app="maelstro.main:app",
        host="0.0.0.0",
        port=8000,
        workers=None,  # to be configured
        root_path="",
        # proxy_headers=proxy_headers,
        log_config=get_uvicorn_log_config(),
    )


if __name__ == "__main__":
    docker_dev()
