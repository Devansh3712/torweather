#!/usr/bin/env python
import logging
import os
import pickle
from typing import Any
from typing import List

import requests  # type: ignore
from pymongo import MongoClient
from pymongo.collection import Collection
from requests.structures import CaseInsensitiveDict  # type: ignore

from torweather.config import secrets
from torweather.exceptions import InvalidFingerprintError
from torweather.schemas import RelayData


class Relay:
    """Class for fetching data of a relay using the onionoo API and
    maintaining the MongoDB database.

    Attributes:
        fingerprint (str): Fingerprint of the relay.
        email (str): Email for subscribing to TOR weather service.
    """

    def __init__(self, fingerprint: str, email: str, testing: bool = False) -> None:
        """Initializes the Relay class with the fields to be fetched by the
        onionoo API and a custom logger."""
        # A TOR relay's fingerprint is a 40 digit hexadecimal string.
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
        if testing:
            self.__database = self.__client["testtorweather"]
        else:
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
    def logger(self) -> logging.Logger:
        """Returns the logger object."""
        return self.__logger

    @property
    def data(self):
        """Returns data of the relay as a pydantic model."""
        return self.__fetch_data()

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

    def __fetch_data(self) -> RelayData:
        """Fetch data of the relay using the onionoo API.

        Returns:
            RelayData: Pydantic model of relay data.
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
                raise InvalidFingerprintError(self.fingerprint)
        result[0]["email"] = self.email
        return RelayData(**result[0])

    def subscribe(self) -> bool:
        """Subscribe to the TOR weather service.

        On subscribing, a document is inserted into the MongoDB database,
        with the fingerprint of the relay and pickled relay data.

        Returns:
            bool: False if relay fingerprint exists in collection else True.
        """
        # If the current fingerprint exists in a document in the `torweather`
        # collection.
        if self.collection.find_one({"fingerprint": self.fingerprint}):
            return False
        # Store the relay data as a pydantic model object in the subscribers
        # collection.
        relay_data = pickle.dumps(self.data)  # Pickle the RelayData object.
        self.collection.insert_one(
            {"data": relay_data, "fingerprint": self.data.fingerprint}
        )
        self.logger.info(
            f"Node {self.data.nickname} (fingerprint: {self.data.fingerprint}) subscribed."
        )
        return True

    def unsubscribe(self) -> bool:
        """Unsubscribe from the TOR weather service.

        On unsubscribing, the document with current relay's fingerprint is
        deleted from the MongoDB database.

        Returns:
            bool: False if relay fingerprint does not exist in collection else True.
        """
        # If the current fingerprint does not exist in a document in the
        # `torweather` collection.
        if not self.collection.find_one({"fingerprint": self.fingerprint}):
            return False
        document = self.collection.find_one({"fingerprint": self.fingerprint})
        relay_data = pickle.loads(document["data"])  # Unpickle the RelayData object.
        self.collection.delete_one({"fingerprint": self.fingerprint})
        self.logger.info(
            f"Node {relay_data.nickname} (fingerprint: {relay_data.fingerprint}) unsubscribed."
        )
        return True

    def update(self):
        """Update the relay data in the MongoDB database."""
        updated_relay_values = pickle.dumps(self.data)
        self.collection.update_one(
            {"fingerprint": self.fingerprint}, {"$set": {"data": updated_relay_values}}
        )
