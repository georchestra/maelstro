import requests
from typing import BinaryIO

class GNSession:
    def __init__(self, apiUrl: str, user: str, pw: str):
        self._apiUrl = apiUrl
        self._user = user
        self._pw = pw
        self._session = requests.Session()
        # only with gateway ...
        # self._session.post(f"{gateway_url}/login", data={"username": user, "password": pw})
        r = self._session.get(f"{self._apiUrl}/me", headers={"Accept": "application/json"}, auth=(user, pw))
        if r.status_code == 200:
            jj = r.json()
            print(f"Connected as {jj['name']} {jj['surname']} with profile {jj['profile']}")
        else:
            r = self._session.get(f"{self._apiUrl}/me", headers={"Accept": "application/json"})
            if r.status_code == 204:
                print("Not connected")
            else:
                raise Exception(f"Error in basic auth - status_code: {r.status_code} - error: {r.text}")

    def getUserInfo(self):
        return self._session.get(f"{self._apiUrl}/me", headers={"Accept": "application/json"}).json()

    def getRecordIds(self):
        return [i['_id'] for i in self._session.post(f"{self._apiUrl}/search/records/_search", headers={"Accept": "application/json"}, json={}).json()['hits']['hits']]

    def getRecordZip(self, uuid: str):
        r = self._session.get(f"{self._apiUrl}/records/{uuid}", headers={"Accept": "application/zip"})
        if r.status_code == 200:
            return r.content

    def getRecordXml(self, uuid: str):
        r = self._session.get(f"{self._apiUrl}/records/{uuid}", headers={"Accept": "application/xml"})
        if r.status_code == 200:
            return r.content

    def uploadRecordZip(self, zipFile: BinaryIO, overwrite: bool = True):
        return self._session.post(f"{self._apiUrl}/records", headers={"X-XSRF-TOKEN": self._session.cookies.get('XSRF-TOKEN', path='/geonetwork'), "Accept": "application/json"}, files={"file": ("file.zip", zipFile, "application/zip")}, params={"metadataType": "METADATA", "uuidProcessing": "OVERWRITE" if overwrite else "GENERATEUUID"}, auth=(self._user, self._pw))

    def uploadRecordXml(self, xmlFile: BinaryIO, overwrite=True):
        return self._session.post(f"{self._apiUrl}/records", headers={"X-XSRF-TOKEN": self._session.cookies.get('XSRF-TOKEN', path='/geonetwork'), "Accept": "application/json"}, files={"file": ("file.xml", xmlFile, "application/zip")}, params={"metadataType": "METADATA", "uuidProcessing": "OVERWRITE" if overwrite else "GENERATEUUID"}, auth=(self._user, self._pw))
