#!/usr/bin/env python
from collections.abc import MutableMapping
from typing import Any
from typing import List

import requests  # type: ignore
from pymongo import MongoClient
from pymongo.collection import Collection
from requests.structures import CaseInsensitiveDict  # type: ignore

from torweather.config import secrets
from torweather.schemas import RelayData


class Relay:
    def __init__(self, fingerprint: str, email: str) -> None:
        assert len(fingerprint) == 40
        self._fingerprint: str = fingerprint
        self._email: str = email
        self.fields: List[str] = [
            "nickname",
            "fingerprint",
            "last_seen",
            "running",
            "last_restarted",
            "effective_family",
            "version_status",
        ]
        self._url: str = "https://onionoo.torproject.org/details"
        self._client = MongoClient(secrets.MONGODB_URI)
        self._database = self._client["torweather"]
        self._collection = self._database["subscribers"]

    @property
    def fingerprint(self) -> str:
        return self._fingerprint

    @property
    def email(self) -> str:
        return self._email

    @property
    def url(self) -> str:
        return self._url

    @property
    def collection(self) -> Collection:
        return self._collection

    def _fetch_data(self) -> MutableMapping[str, Any]:
        with requests.Session() as session:
            session.headers = CaseInsensitiveDict(  # type: ignore
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko)Chrome/94.0.4606.81 Safari/537.36"
                }
            )
            response = session.get(
                f"{self.url}?search={self.fingerprint}&fields={','.join(self.fields)}"
            )
            result = response.json()["relays"]
            if response.status_code != 200 or not result:
                raise
        return result[0]

    def subscribe(self) -> bool:
        # If the current fingerprint exists in a document in the `torweather`
        # collection.
        if self.collection.find_one({"fingerprint": self.fingerprint}):
            return False
        relay_data = self._fetch_data()
        relay_data["email"] = self.email
        self.collection.insert_one(relay_data)
        return True

    def unsubscribe(self) -> bool:
        # If the current fingerprint does not exist in a document in the
        # `torweather` collection.
        if not self.collection.find_one({"fingerprint": self.fingerprint}):
            return False
        self.collection.delete_one({"fingerprint": self.fingerprint})
        return True

    def _update(self) -> bool:
        updates_relay_values = self._fetch_data()
        self.collection.update_one(
            {"fingerprint": self.fingerprint}, {"$set": updates_relay_values}
        )
        return True
