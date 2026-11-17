import os
import logging
from unittest.mock import patch

import pytest
import requests
import requests_mock

from maelstro.core import CopyManager
from maelstro.core.operations import LogCollectionHandler
from maelstro.core.georchestra import GeorchestraHandler, get_georchestra_handler
from maelstro.common.models import GsApiRecord, InfoRecord


def test_geoserver_session_logging():
    service_info = {
        "url": "https://example.test/geoserver",
        "auth": ("user", "password"),
    }
    with patch.object(GeorchestraHandler, "get_service_info", return_value=service_info):
        with requests_mock.Mocker() as mocked:
            mocked.get(
                "https://example.test/geoserver/rest/about/version.json",
                json={"about": {"resource": [{"@name": "GeoServer", "Version": "2.28"}]}},
            )
            with get_georchestra_handler() as handler:
                handler.get_gs_service("test", True)
                records = handler.log_handler.responses
                assert len(records) == 2
                assert isinstance(records[0], GsApiRecord)
                assert isinstance(records[1], InfoRecord)
                assert "Session opened on" in records[1].message


@pytest.mark.parametrize("logger_name", ["GS Session", "geoservercloud"])
def test_geoserver_operation_classification(logger_name):
    handler = LogCollectionHandler()
    response = requests.Response()
    response.status_code = 200
    response.url = "https://example.test/geoserver/rest/layers.json"
    response.request = requests.Request("GET", response.url).prepare()
    record = logging.LogRecord(logger_name, logging.INFO, __file__, 0, "GET", (), None)
    record.response = response

    handler.emit(record)

    assert isinstance(handler.responses[0], GsApiRecord)
    assert handler.get_json_responses()[0]["type"] == "gs_api"


def test_unformatted_log_message():
    handler = LogCollectionHandler()
    record = logging.LogRecord(
        "geoservercloud", logging.INFO, __file__, 0, "Session opened on %s", ("test",), None
    )

    handler.emit(record)

    assert isinstance(handler.responses[0], InfoRecord)
    assert handler.responses[0].message == "Session opened on test"


def test_copy_123_iso19139():
    log_handler = LogCollectionHandler()
    geo_hnd = GeorchestraHandler(log_handler)

    with open(os.path.join(os.path.dirname(__file__), 'demo_iso19139.zip'), 'rb') as zf:
        zbytes = zf.read()

    with requests_mock.Mocker() as m:
        m.get(
            "https://demo.georchestra.org/geonetwork/srv/api/site",
            json={'system/platform/version': '4.2.2'}
        )
        m.get(
            "https://georchestra-127-0-0-1.nip.io/geonetwork/srv/api/site",
            json={'system/platform/version': '4.2.2'}
        )
        m.get(
            "https://demo.georchestra.org/geonetwork/srv/api/records/123",
            content=zbytes,
        )
        m.post(
            "https://georchestra-127-0-0-1.nip.io/geonetwork/srv/api/records?metadataType=METADATA&uuidProcessing=OVERWRITE",
            json={"errors": [], "metadataInfos": {101: [{"uuid": "101"}]}}
        )
        m.get(
            "https://georchestra-127-0-0-1.nip.io/geonetwork/srv/api/records/101",
            json={"gmd:fileIdentifier": {"gco:CharacterString": {"#text": "dummy_uuid"}}}
        )
        copy_mgr = CopyManager('GeonetworkMaster', 'CompoLocale', '123', geo_hnd)
        success = copy_mgr.copy_dataset(True, False, False)
        assert success == "Metadata creation successful (dummy_uuid)"


def test_copy_123_iso19115():
    log_handler = LogCollectionHandler()
    geo_hnd = GeorchestraHandler(log_handler)

    with open(os.path.join(os.path.dirname(__file__), 'lille_iso19115-3.zip'), 'rb') as zf:
        zbytes = zf.read()

    with requests_mock.Mocker() as m:
        m.get(
            "https://demo.georchestra.org/geonetwork/srv/api/site",
            json={'system/platform/version': '4.2.2'}
        )
        m.get(
            "https://georchestra-127-0-0-1.nip.io/geonetwork/srv/api/site",
            json={'system/platform/version': '4.2.2'}
        )
        m.get(
            "https://demo.georchestra.org/geonetwork/srv/api/records/123",
            content=zbytes,
        )
        m.post(
            "https://georchestra-127-0-0-1.nip.io/geonetwork/srv/api/records?metadataType=METADATA&uuidProcessing=OVERWRITE",
            json={"errors": [], "metadataInfos": {101: [{"uuid": "101"}]}}
        )
        m.get(
            "https://georchestra-127-0-0-1.nip.io/geonetwork/srv/api/records/101",
            json={"mdb:metadataIdentifier": {"mcc:MD_Identifier": {"mcc:code": {"gco:CharacterString":{"#text": "dummy_uuid"}}}}}
        )
        copy_mgr = CopyManager('GeonetworkMaster', 'CompoLocale', '123', geo_hnd)
        success = copy_mgr.copy_dataset(True, False, False)
        assert success == "Metadata creation successful (dummy_uuid)"
