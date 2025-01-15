import sys
import logging
from typing import BinaryIO
import requests


logger = logging.getLogger("FastAPI")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        "{asctime} - {name}:{levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )
)
logger.addHandler(handler)


class GNSession:
    def __init__(self, api_url: str, user: str, pw: str):
        self._api_url = api_url
        self._user = user
        self._pw = pw
        self._session = requests.Session()
        # only with gateway ...
        # self._session.post(f"{gateway_url}/login", data={"username": user, "password": pw})
        r = self._session.get(
            f"{self._api_url}/me",
            headers={"Accept": "application/json"},
            auth=(user, pw),
        )
        if r.status_code == 200:
            jj = r.json()
            print("bla")
            logger.info(
                "Connected as %s %s with profile %s",
                jj["name"],
                jj["surname"],
                jj["profile"],
            )
        else:
            r = self._session.get(
                f"{self._api_url}/me", headers={"Accept": "application/json"}
            )
            if r.status_code == 204:
                logging.info("Not connected")
            else:
                raise ConnectionError(
                    f"Error in basic auth - status_code: {r.status_code} - error: {r.text}"
                )

    def get_user_info(self):
        return self._session.get(
            f"{self._api_url}/me", headers={"Accept": "application/json"}
        ).json()

    def get_record_ids(self):
        return [
            i["_id"]
            for i in self._session.post(
                f"{self._api_url}/search/records/_search",
                headers={"Accept": "application/json"},
                json={},
            ).json()["hits"]["hits"]
        ]

    def get_record_zip(self, uuid: str) -> bytes:
        r = self._session.get(
            f"{self._api_url}/records/{uuid}", headers={"Accept": "application/zip"}
        )
        if r.status_code == 200:
            return r.content
        return b""

    def get_record_xml(self, uuid: str) -> bytes:
        r = self._session.get(
            f"{self._api_url}/records/{uuid}", headers={"Accept": "application/xml"}
        )
        if r.status_code == 200:
            return r.content
        return b""

    def upload_record_zip(self, zip_file: BinaryIO, overwrite: bool = True):
        return self._session.post(
            f"{self._api_url}/records",
            headers={
                "X-XSRF-TOKEN": self._session.cookies.get(
                    "XSRF-TOKEN", path="/geonetwork"
                ),
                "Accept": "application/json",
            },
            files={"file": ("file.zip", zip_file, "application/zip")},
            params={
                "metadataType": "METADATA",
                "uuidProcessing": "OVERWRITE" if overwrite else "GENERATEUUID",
            },
            auth=(self._user, self._pw),
        )

    def upload_record_xml(self, xml_file: BinaryIO, overwrite=True):
        return self._session.post(
            f"{self._api_url}/records",
            headers={
                "X-XSRF-TOKEN": self._session.cookies.get(
                    "XSRF-TOKEN", path="/geonetwork"
                ),
                "Accept": "application/json",
            },
            files={"file": ("file.xml", xml_file, "application/zip")},
            params={
                "metadataType": "METADATA",
                "uuidProcessing": "OVERWRITE" if overwrite else "GENERATEUUID",
            },
            auth=(self._user, self._pw),
        )
