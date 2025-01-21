#!/usr/local/bin/python

import requests


def check():
    assert requests.get("http://localhost:8000/health").status_code == 200
