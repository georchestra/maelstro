import os
import requests_mock

from maelstro.core import CopyManager
from maelstro.core.operations import LogCollectionHandler
from maelstro.core.georchestra import GeorchestraHandler


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
