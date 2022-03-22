#!/usr/bin/env python
import logging
import os
from collections.abc import Sequence
from typing import Any

import requests  # type: ignore
from pymongo import MongoClient
from pymongo.collection import Collection
from requests.structures import CaseInsensitiveDict  # type: ignore

from torweather.config import secrets
from torweather.exceptions import InvalidFingerprintError
from torweather.schemas import Notif
from torweather.schemas import RelayData


class Relay:
    """Class for fetching data of a relay using the onionoo API and
    maintaining the MongoDB database.

    In the MongoDB database, a document with relay's fingerprint and
    the email of relay provider is saved.

    Attributes:
        fingerprint (str): Fingerprint of the relay.
        email (Sequence[str]): Email(s) for subscribing to TOR weather service.
        notifs (Sequence[Notif]): Notifications to subscribe to.
    """

    def __init__(
        self,
        fingerprint: str,
        email: Sequence[str],
        notifs: Sequence[Notif],
        testing: bool = False,
    ) -> None:
        """Initializes the Relay class with the fields to be fetched by the
        onionoo API and a custom logger."""
        self.fingerprint: str = fingerprint
        self.email: Sequence[str] = email
        self.notifs: Sequence[Notif] = notifs
        # Fields to fetch for a relay from the onionoo API.
        self.__fields: Sequence[str] = [
            "nickname",
            "fingerprint",
            "last_seen",
            "running",
            "consensus_weight",
            "last_restarted",
            "bandwidth_rate",
            "effective_family",
            "version_status",
            "recommended_version",
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
        with the fingerprint of the relay and the email to subscribe to.

        Returns:
            bool: False if relay fingerprint exists in collection else True.
        """
        # If the current fingerprint exists in a document in the `torweather`
        # collection.
        if self.collection.find_one({"fingerprint": self.fingerprint}):
            return False
        # Create a dictionary with enum variable name as key and False as value.
        # This dictionary will be used to keep track of notifications sent, thus
        # the default value is False.
        _notifs = {notif.name: False for notif in self.notifs}
        self.collection.insert_one(
            {
                "fingerprint": self.data.fingerprint,
                "email": self.data.email,
                "notifs": _notifs,
            }
        )
        self.logger.info(
            f"Node {self.data.nickname} (fingerprint: {self.data.fingerprint}) subscribed to "
            f"{', '.join(_notifs.keys())} notifications."
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
        self.collection.delete_one({"fingerprint": self.fingerprint})
        self.logger.info(
            f"Node {self.data.nickname} (fingerprint: {self.data.fingerprint}) unsubscribed."
        )
        return True
