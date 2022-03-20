#!/usr/bin/env python
import logging
import os
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
        """Initializes the Email class with the fields to be fetched by the
        onionoo API and a custom logger."""
        assert len(fingerprint) == 40
        self.fingerprint: str = fingerprint
        self.email: str = email
        self.__fields: List[str] = [
            "nickname",
            "fingerprint",
            "last_seen",
            "running",
            "last_restarted",
            "effective_family",
            "version_status",
        ]
        self.__url: str = "https://onionoo.torproject.org/details"
        self.__client = MongoClient(secrets.MONGODB_URI)
        self.__database = self.__client["torweather"]
        self.__collection = self.__database["subscribers"]
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)
        self.__set_logging_handler()

    @property
    def url(self) -> str:
        """Returns the onionoo service URL."""
        return self.__url

    @property
    def collection(self) -> Collection:
        """Returns the MongoDB collection object."""
        return self.__collection

    @property
    def logger(self):
        """Returns the logger object."""
        return self.__logger

    @property
    def data(self):
        """Returns data of the relay as a pydantic model."""
        relay_data = self.__fetch_data()
        return RelayData(**relay_data)

    def __set_logging_handler(self) -> None:
        """Creates and sets a file handler for the custom logger."""
        current_directory: str = os.path.dirname(os.path.realpath(__file__))
        if not os.path.isdir(os.path.join(current_directory, "logs")):
            os.mkdir(os.path.join(current_directory, "logs"))
        handler = logging.FileHandler(
            os.path.join(current_directory, "logs", "relay.log")
        )
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(levelname)s: %(asctime)s - %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def __fetch_data(self) -> MutableMapping[str, Any]:
        """Fetch data of the relay using the onionoo API.

        Returns:
            MutableMapping[str, Any]: Dictionary of relay data.
        """
        with requests.Session() as session:
            session.headers = CaseInsensitiveDict(  # type: ignore
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko)Chrome/94.0.4606.81 Safari/537.36"
                }
            )
            response = session.get(
                f"{self.url}?search={self.fingerprint}&fields={','.join(self.__fields)}"
            )
            result = response.json()["relays"]
            if response.status_code != 200 or not result:
                raise
        result[0]["email"] = self.email
        return result[0]

    def subscribe(self) -> bool:
        """Subscribe to the TOR weather service.

        Returns:
            bool: False if relay fingerprint exists in collection else True.
        """
        # If the current fingerprint exists in a document in the `torweather`
        # collection.
        if self.collection.find_one({"fingerprint": self.fingerprint}):
            return False
        relay_data = self.__fetch_data()
        self.collection.insert_one(relay_data)
        self.logger.info(
            f"Node {relay_data['nickname']} (fingerprint: {relay_data['fingerprint']}) subscribed."
        )
        return True

    def unsubscribe(self) -> bool:
        """Unsubscribe from the TOR weather service.

        Returns:
            bool: False if relay fingerprint does not exist in collection else True.
        """
        # If the current fingerprint does not exist in a document in the
        # `torweather` collection.
        if not self.collection.find_one({"fingerprint": self.fingerprint}):
            return False
        relay_data = self.collection.find_one({"fingerprint": self.fingerprint})
        self.collection.delete_one({"fingerprint": self.fingerprint})
        self.logger.info(
            f"Node {relay_data['nickname']} (fingerprint: {relay_data['fingerprint']}) unsubscribed."
        )
        return True

    def __update(self):
        """Update relay data."""
        updated_relay_values = self.__fetch_data()
        self.collection.update_one(
            {"fingerprint": self.fingerprint}, {"$set": updated_relay_values}
        )
