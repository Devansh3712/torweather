#!/usr/bin/env python
from collections.abc import Mapping
from typing import Any
from typing import List

import requests  # type: ignore
from pymongo import MongoClient
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

    @property
    def fingerprint(self) -> str:
        return self._fingerprint

    @property
    def email(self) -> str:
        return self._email

    @property
    def url(self) -> str:
        return self._url

    def _fetch_data(self) -> Mapping[str, Any]:
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
            if response.status_code != 200 or result == []:
                raise
        return result[0]
