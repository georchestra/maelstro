#!/usr/local/bin/python

import requests


def check() -> None:
    assert (
        requests.get("http://localhost:8000/health").status_code == 200
    )  # pylint: disable=missing-timeout
