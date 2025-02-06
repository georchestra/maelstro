import pytest
from fastapi.testclient import TestClient

from maelstro.main import app


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'Hello': 'World'}


@pytest.mark.mo0
def test_debug_():
    response = client.post("/debug", json={'query': {}}, headers={"accept": "application/json"})
    assert response.status_code == 200
    assert len(response.json()) == 13


@pytest.mark.mo2
def test_search_2():
    response = client.post("/search/GeonetworkGAM", json={'query': {
        "query_string": {
            "query": "*"
        }}}, headers={"accept": "application/json"})
    assert response.status_code == 400
    assert list(response.json()['detail']['content'].keys()) == ['info_0', 'Request:', 'Error:']




@pytest.mark.mo1
def test_search_():
    response = client.post("/search/GeonetworkGAM", json={'query': {}}, headers={"accept": "application/json"})
    assert response.status_code == 400
    assert list(response.json()['detail']['content'].keys()) == ['info_0', 'Request:', 'Error:']


@pytest.mark.mo
def test_copy__():
    response = client.put("/copy?src_name=GeonetworkGAM&dst_name=CompoLocale&metadataUuid=269f8f0c-7695-43f3-9239-f6e39eba59fd0&copy_meta=true&copy_layers=false&copy_styles=true", headers={"accept": "application/json"})
    assert response.status_code == 200
    assert len(response.json()) == 15


@pytest.mark.mox
def test_copy_():
    response = client.put("/copy?src_name=GeonetworkGAM&dst_name=CompoLocale&metadataUuid=269f8f0c-7695-43f3-9239-f6e39eba59fd&copy_meta=true&copy_layers=true&copy_styles=false&dry_run=false", headers={"accept": "application/json"})
    assert response.status_code == 200
    assert len(response.json()) == 15


@pytest.mark.skip("Search on demo server currently down")
def test_search():
    response = client.post("/search/GeonetworkDemo", json={})
    assert response.json()['hits']['total'] == {'value': 8316, 'relation': 'eq'}


@pytest.mark.skip("Search on demo server currently down")
def test_search2():
    response = client.post("/search/GeonetworkDemo", json={"query": {"wildcard": {"resourceTitleObject.default": {"value": "plan_*"}}}, "size": 1})
    assert len(response.json()['hits']['hits']) == 1
    assert response.json()['hits']['total'] == 2


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
