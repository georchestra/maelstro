from maelstro.common.types import Credentials
from maelstro.core.datafeeder import ADMIN_PATH, DatafeederManager
from maelstro.core.operations import LogCollectionHandler


def test_preview_and_streamed_copy(monkeypatch, requests_mock):
    source_url = "https://source.example/datafeeder-backend"
    target_url = "https://target.example/datafeeder-backend"

    def access_info(is_src, _instance_id):
        return {
            "url": source_url if is_src else target_url,
            "auth": Credentials("admin", "password"),
            "verifytls": True,
        }

    monkeypatch.setattr(
        "maelstro.core.datafeeder.config.get_datafeeder_access_info", access_info
    )
    link = {"id": "link-id", "metadata_id": "metadata-id"}
    exported = {
        **link,
        "source_import_type": "file",
        "final_table_name": "roads",
        "integrity_organization": "PSC",
    }
    requests_mock.get(f"{source_url}/{ADMIN_PATH}/by-metadata/metadata-id", json=link)
    requests_mock.get(f"{source_url}/{ADMIN_PATH}/link-id/export", json=exported)
    requests_mock.get(
        f"{target_url}/{ADMIN_PATH}/by-metadata/metadata-id", status_code=404
    )
    requests_mock.get(
        f"{target_url}/{ADMIN_PATH}/data/PSC/roads",
        json={"exists": False, "used_by": None},
    )
    requests_mock.get(
        f"{source_url}/{ADMIN_PATH}/link-id/data", content=b"streamed table"
    )
    uploaded = {}

    def accept_upload(request, _context):
        uploaded["body"] = b"".join(request.body)
        return {"row_count": 12}

    requests_mock.put(f"{target_url}/{ADMIN_PATH}/data/PSC/roads", json=accept_upload)
    requests_mock.post(
        f"{target_url}/{ADMIN_PATH}/import",
        json={"integrity_link_id": "target-link-id", "mode": "attach"},
    )

    manager = DatafeederManager("source", "target", LogCollectionHandler())
    preview, _ = manager.preview("metadata-id")

    assert preview.action == "copy_table"
    assert manager.copy("metadata-id") == "Datafeeder dataset imported (target-link-id)"
    assert uploaded["body"] == b"streamed table"


def test_copy_is_resumable_when_dataset_was_already_imported(
    monkeypatch, requests_mock
):
    source_url = "https://source.example/datafeeder-backend"
    target_url = "https://target.example/datafeeder-backend"

    monkeypatch.setattr(
        "maelstro.core.datafeeder.config.get_datafeeder_access_info",
        lambda is_src, _instance_id: {
            "url": source_url if is_src else target_url,
            "auth": None,
            "verifytls": True,
        },
    )
    link = {"id": "source-link", "metadata_id": "metadata-id"}
    requests_mock.get(f"{source_url}/{ADMIN_PATH}/by-metadata/metadata-id", json=link)
    requests_mock.get(
        f"{source_url}/{ADMIN_PATH}/source-link/export",
        json={
            **link,
            "source_import_type": "file",
            "final_table_name": "roads",
            "integrity_organization": "PSC",
        },
    )
    requests_mock.get(
        f"{target_url}/{ADMIN_PATH}/by-metadata/metadata-id",
        json={"id": "target-link", "metadata_id": "metadata-id"},
    )

    manager = DatafeederManager("source", "target", LogCollectionHandler())

    assert manager.copy("metadata-id") == "Datafeeder dataset already imported"
    assert requests_mock.call_count == 3
