import os
import re
import json
import pytest
from pytest_unordered import unordered
from unittest.mock import patch
import requests_mock
from requests.exceptions import HTTPError

from maelstro.core.copy_manager import CopyManager
from maelstro.core.georchestra import get_georchestra_handler
from maelstro.common.exceptions import MaelstroException


@pytest.fixture()
def GN_site():
    return {"system/platform/version": "4.4.4"}


@pytest.fixture()
def GN_record_zip():
    with open(os.path.join(os.path.dirname(__file__), "demo_iso19139.zip"), "rb") as f:
        return f.read()


@pytest.fixture()
def GN_record(GN_record_zip):
    def create_response_callback(request, context):
        if request.headers.get("accept") == "application/zip":
            return GN_record_zip
        elif request.headers.get("accept") == "application/json":
            return json.dumps(
                {
                    "gmd:fileIdentifier": {
                        "gco:CharacterString": {"#text": "velo_ID"}
                    }
                }
            ).encode()
    return create_response_callback


@pytest.fixture()
def GS_velo_layer():
    return lambda request, context: {
        "layer": {
            "name": "trp_doux:reparation_velo",
            "type": "VECTOR",
            "defaultStyle": {
                "name": "point",
                "href": f"https://{request.hostname}/geoserver/rest/styles/point.json"
            },
            "styles": {
                "@class": "linked-hash-set",
                "style": [
                    {
                        "name": "style1",
                        "href": f"https://{request.hostname}/geoserver/rest/styles/style1.json"
                    },
                    {
                        "name": "style2",
                        "workspace": "ws",
                        "href": f"https://{request.hostname}/geoserver/rest/workspaces/ws/styles/style2.json"
                    }
                ]
            },
            "resource": {
                "@class": "featureType",
                "name": "ws:velo",
                "href": f"https://{request.hostname}/geoserver/rest/workspaces/ws/datastores/ds/featuretypes/velo.json"
            },
            "queryable": True,
            "opaque": False,
            "attribution": {
                "title": "Test Dummy",
                "href": "https://www.test.org/",
                "logoWidth": 0,
                "logoHeight": 0
            },
            "dateCreated": "2024-12-13 13:21:24.38 UTC",
            "dateModified": "2025-01-30 18:58:16.878 UTC"
        }
    }


@pytest.fixture()
def GS_velo_feature():
    return lambda request, context: {
        "featureType": {
            "name": "velo",
            "nativeName": "velos",
            "namespace": {
                "name": "ns",
                "href": f"https://{request.hostname}/geoserver/rest/namespaces/ns.json"
            },
            "title": "velos",
            "abstract": "velos",
            "metadataLinks": {
                "metadataLink": [
                    {
                        "type": "text/xml",
                        "metadataType": "ISO19115:2003",
                        "content": "https://demo.georchestra.org/geonetwork/srv/api/records/ef6fe5e6-b8f8-49c4-a885-69ce665515dc/formatters/xml"
                    },
                ]
            },
            "store": {
                "@class": "dataStore",
                "name": "ws:ds",
                "href": f"https://{request.hostname}/geoserver/rest/workspaces/ws/datastores/ds.json"
            },
        }
    }


@pytest.fixture()
def GS_style_info():
    return {
        "style": {
            "name": "dummy_style",
            "format": "sld",
            "workspace": {"name": "ws"},
            "languageVersion": "fr",
            "filename": "file",
        }
    }


@pytest.fixture()
def GS_datastore():
    return lambda request, context: {
        "dataStore": {
            "name": "dummy_datastore",
            "description": "Datafeeder uploaded datasets",
            "type": "PostGIS (JNDI)",
            "enabled": True,
            "workspace": {
                "name": "ws",
                "href": f"https://{request.hostname}/geoserver/rest/workspaces/ws.json"
            },
        }
     }


@pytest.fixture()
def GS_workspace():
    return {
        "workspace": {
            "name": "dummy_workspace",
        }
     }


@pytest.fixture()
def api_mock():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture()
def GN_mock(api_mock, GN_site, GN_record):
    api_mock.get(re.compile(r"https://.*/geonetwork/srv/api/site"), json=GN_site)
    api_mock.get(re.compile(r"https://.*/geonetwork/srv/api/records/[^/]*"), content=GN_record)
    api_mock.post(re.compile(r"https://.*/geonetwork/srv/api/records"), json={
        "errors": [],
        "metadataInfos": {"velo_data": [{"uuid": "uuid1"}]},
    })
    return api_mock


@pytest.fixture()
def GS_mock(api_mock, GS_velo_layer):
    api_mock.get(re.compile(r"https://.*/geoserver/rest/about/version.json"), json={
            "about": {"resource": [{"@name": "mock_geoserver", "Version": "1.1.1"}]},
    })
    api_mock.get(re.compile(r"https://.*/geoserver/rest/layers/trp_doux:reparation_velo(.json)?"), json=GS_velo_layer)
    api_mock.put(re.compile(r"https://.*/geoserver/rest/layers/trp_doux:reparation_velo"), json={"OK": True})
    return api_mock


@pytest.fixture()
def GS_no_dst_resource(api_mock):
    api_mock.get(re.compile(r"https://georchestra-127-0-0-1.nip.io/geoserver/rest/workspaces/ws/datastores/ds/featuretypes/velo.(json|xml)"), status_code=404)
    return api_mock


@pytest.fixture()
def GS_no_dst_style(api_mock):
    api_mock.get(re.compile(r"https://georchestra-127-0-0-1.nip.io/geoserver/rest/(workspaces/[^/]*/)?styles/.*.(json|sld)"), status_code=404)
    return api_mock


@pytest.fixture()
def GS_no_dst_ds(api_mock):
    api_mock.put(re.compile(r"https://.*/geoserver/rest/(workspaces/[^/]*/)?styles/.*.(json|sld)"), status_code=404)
    api_mock.put(re.compile(r"https://.*/geoserver/rest/workspaces/ws/datastores/ds/featuretypes"), status_code=404)
    api_mock.get("https://georchestra-127-0-0-1.nip.io/geoserver/rest/workspaces/ws/datastores/ds.json", status_code=404)
    return api_mock


@pytest.fixture()
def GS_no_dst_ws(api_mock):
    api_mock.put(re.compile(r"https://.*/geoserver/rest/(workspaces/[^/]*/)?styles/.*.(json|sld)"), status_code=404)
    api_mock.put(re.compile(r"https://.*/geoserver/rest/workspaces/ws/datastores/ds/featuretypes"), status_code=404)
    api_mock.get("https://georchestra-127-0-0-1.nip.io/geoserver/rest/workspaces/ws.json", status_code=404)
    return api_mock


@pytest.fixture()
def GS_WS(api_mock, GS_velo_feature, GS_style_info, GS_datastore, GS_workspace):
    api_mock.get(re.compile(r"https://.*/geoserver/rest/workspaces/ws/datastores/ds/featuretypes/velo.(json|xml)$"), json=GS_velo_feature)
    api_mock.put(re.compile(r"https://.*/geoserver/rest/workspaces/ws/datastores/ds/featuretypes/velo.(json|xml)$"), json={"OK": True})
    api_mock.post(re.compile(r"https://.*/geoserver/rest/workspaces/ws/datastores/ds/featuretypes$"), json={"OK": True})
    api_mock.get(re.compile(r"https://.*/geoserver/rest/workspaces/ws/datastores/ds.json$"), json=GS_datastore)
    api_mock.get(re.compile(r"https://.*/geoserver/rest/workspaces/ws.json"), json=GS_workspace)
    api_mock.get(re.compile(r"https://.*/geoserver/rest/(workspaces/[^/]*/)?styles/.*.(json|sld)$"), headers={"content-type": "application/json"}, json=GS_style_info)
    api_mock.put(re.compile(r"https://.*/geoserver/rest/(workspaces/[^/]*/)?styles/.*.(json|sld)$"), json={"OK": True})
    api_mock.post(re.compile(r"https://.*/geoserver/rest/(workspaces/[^/]*/)?styles$"), json={"OK": True})
    return api_mock


@pytest.fixture()
def geo_hnd():
    with get_georchestra_handler() as geo_hnd:
        yield geo_hnd


@pytest.fixture()
def copy_manager(geo_hnd, GN_mock, GS_mock, GS_WS):
    def patch_config(config):
        config.config["sources"]["geoserver_instances"] = [
            {"url": "https://public.sig.rennesmetropole.fr/geoserver"},
        ]
        return ["https://public.sig.rennesmetropole.fr/geoserver"]

    with patch("maelstro.config.config.Config.get_gs_sources", patch_config):
        yield CopyManager("GeonetworkMaster", "CompoLocale", "ef6fe5e6-b8f8-49c4-a885-69ce665515dc", geo_hnd)


def test_copy_preview(copy_manager):
    cm = copy_manager
    prev = cm.copy_preview(True, True, True)
    preview_ref = {
        "geonetwork_resources": unordered([
            {
                'src': 'GeonetworkMaster',
                'dst': 'CompoLocale',
                'metadata': unordered([
                    {
                        'title': 'Stations de réparation et gonflage pour vélo sur Rennes Métropole',
                        'iso_standard': 'iso19139',
                    }
                ])
            }
        ]),
        'geoserver_resources': unordered([
            {
                'src': 'https://public.sig.rennesmetropole.fr/geoserver',
                'dst': 'https://georchestra-127-0-0-1.nip.io/geoserver',
                'layers': ['trp_doux:reparation_velo'],
                'styles': unordered(['point', 'style1', 'style2']),
            }
        ])
    }
    assert prev.model_dump() == preview_ref


def test_copy_dataset_base(copy_manager, api_mock, GS_WS):
    cm = copy_manager
    cm.copy_dataset(True, True, False)
    assert set(h.method for h in api_mock.request_history if "featuretypes" in h.url) == {'GET', 'PUT'}


@pytest.mark.parametrize("copy_styles", [False, True])
def test_copy_dataset_no_rs(copy_styles, copy_manager, api_mock, GS_no_dst_resource):
    cm = copy_manager
    cm.copy_dataset(True, True, copy_styles)
    assert set(h.method for h in api_mock.request_history if "featuretypes" in h.url) == {'GET', 'POST'}
    assert "POST" not in [h.method for h in api_mock.request_history if "styles" in h.url]


def test_copy_dataset_no_style(copy_manager, api_mock, GS_no_dst_style):
    cm = copy_manager
    cm.copy_dataset(True, True, True)
    assert set(h.method for h in api_mock.request_history if "styles" in h.url) == {'GET', 'POST', 'PUT'}


@pytest.mark.parametrize("copy_styles", [False, True])
def test_copy_dataset_no_ds(copy_styles, copy_manager, GS_no_dst_ds):
    cm = copy_manager
    with pytest.raises((MaelstroException, HTTPError)) as exc:
        cm.copy_dataset(True, True, copy_styles)
    if copy_styles:
        # styles do not depend on datastore
        assert isinstance(exc.value, HTTPError)
        assert exc.value.response.status_code == 404
    else:
        assert isinstance(exc.value, MaelstroException)
        assert exc.value.details.err == "Datastore ws:ds not found on destination Geoserver CompoLocale"


@pytest.mark.parametrize("copy_styles", [False, True])
def test_copy_dataset_no_ws(copy_styles, copy_manager, GS_no_dst_ws):
    cm = copy_manager
    with pytest.raises(MaelstroException) as exc:
        cm.copy_dataset(True, True, copy_styles)
    assert exc.value.details.err == "Workspace ws not found on destination Geoserver CompoLocale"
