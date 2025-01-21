#!/usr/local/bin/python

import requests

assert requests.get('http://localhost:8000/health').status_code == 200
