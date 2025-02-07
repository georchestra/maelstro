import pytest
from fastapi.testclient import TestClient

from maelstro.main import app


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'Hello': 'World'}


def test_search():
    response = client.post("/search/GeonetworkDemo", json={})
    assert response.json()['hits']['total']["value"] > 8000


def test_search2():
    response = client.post("/search/GeonetworkDemo", json={"query": {"wildcard": {"resourceTitleObject.default": {"value": "vélo*"}}}, "size": 1})
    assert len(response.json()['hits']['hits']) == 1
    assert response.json()['hits']['total']["value"] == 32


def test_search3():
    response = client.post("/search/GeonetworkRennes", json={"query": {"multi_match": {"fields": ["resourceTitleObject.*"], "query": "plan", "type": "bool_prefix"}}})
    assert len(response.json()['hits']['hits']) == 10
    assert response.json()['hits']['total']['value'] == 22


def test_search4():
    response = client.post("/search/GeonetworkRennes", json={
        "query": {"query_string": {"fields": ["resourceTitleObject.*"], "query": "plan", "type": "bool_prefix"}},
        "size": 15,
    })
    assert len(response.json()['hits']['hits']) == 15
    assert response.json()['hits']['total']['value'] == 22


def test_search5():
    response = client.post("/search/GeonetworkRennes", json={
        "source": [],
        "from_": 0,
        "size": 5
    })
    assert len(response.json()['hits']['hits']) == 5
    assert response.json()['hits']['total']['value'] == 388
