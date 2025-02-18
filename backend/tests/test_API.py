import pytest
from fastapi.testclient import TestClient

import os
os.environ["DEMO_LOGIN"] = "testadmin"

import maelstro.config.config

maelstro.config.config.app_config = maelstro.config.config.Config("/app/dev_config.yaml")

from maelstro.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'Hello': 'World'}


@pytest.mark.skip("test inoperational in CI - OK locally")
def test_search():
    response = client.post("/search/GeonetworkDemo", json={})
    assert response.json()['hits']['total']["value"] > 8000


@pytest.mark.skip("test inoperational in CI - OK locally")
def test_search2():
    response = client.post("/search/GeonetworkDemo", json={"query": {"wildcard": {"resourceTitleObject.default": {"value": "vélo*"}}}, "size": 1})
    assert len(response.json()['hits']['hits']) == 1
    assert response.json()['hits']['total']['value'] == 32


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


@pytest.mark.skip("Depends on extenal data")
def test_search5():
    response = client.post("/search/GeonetworkRennes", json={
        "source": [],
        "from_": 0,
        "size": 5
    })
    assert len(response.json()['hits']['hits']) == 5
    assert response.json()['hits']['total']['value'] > 5


@pytest.mark.skip("test depends on existing workspace 'PSC', so it does not work in CI yet")
def test_copy_all():
    response = client.put("/copy?src_name=GeonetworkDemo&dst_name=CompoLocale&metadataUuid=ef6fe5e6-b8f8-49c4-a885-69ce665515dc&copy_meta=true&copy_layers=true&copy_styles=true", headers={"accept": "application/json"})
    assert response.status_code == 200
    assert len(response.json()) == 24


@pytest.mark.skip("test inoperational in CI")
def test_copy_meta():
    response = client.put("/copy?src_name=GeonetworkRennes&dst_name=CompoLocale&metadataUuid=4d6318d8-de30-4af5-8f37-971c486a0280&copy_meta=true&copy_layers=false&copy_styles=false&dry_run=false", headers={"accept": "application/json"})
    assert response.status_code == 200
    assert len(response.json()) == 7
