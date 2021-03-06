#!/usr/bin/env python
"""Module for fetching, validating relay data and subscribe/unsubscribe them to
Tor Weather service."""
from collections.abc import Mapping
from collections.abc import MutableMapping
from collections.abc import Sequence
from typing import Any

import requests  # type: ignore
from email_validator import validate_email
from pymongo import MongoClient
from pymongo.collection import Collection
from requests.structures import CaseInsensitiveDict  # type: ignore

from torweather.config import secrets
from torweather.exceptions import InvalidEmailError
from torweather.exceptions import InvalidFingerprintError
from torweather.exceptions import NotifNotSubscribedError
from torweather.exceptions import RelayNotSubscribedError
from torweather.exceptions import RelaySubscribedError
from torweather.logger import Logger
from torweather.schemas import Notif
from torweather.schemas import RelayData


class Relay(Logger):
    """Class for fetching data of a relay using the onionoo API and
    managing the MongoDB database.

    Attributes:
        fingerprint (str): Fingerprint of the relay.
        testing (bool): Use a test database for executing functions.
    """

    def __init__(self, fingerprint: str, testing: bool = False) -> None:
        """Initializes the Relay class with the fields to be fetched by the
        onionoo API and a custom logger."""
        super().__init__(__name__)
        self.fingerprint = fingerprint
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
        self.__validate_fingerprint()
        self.__client = MongoClient(secrets.MONGODB_URI)
        self.__database = (
            self.__client["testtorweather"] if testing else self.__client["torweather"]
        )
        self.__collection = self.__database["subscribers"]

    @property
    def url(self) -> str:
        """Returns the onionoo service URL."""
        return self.__url

    @property
    def collection(self) -> Collection:
        """Returns the MongoDB collection object."""
        return self.__collection

    @property
    def data(self):
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
        return RelayData(**result[0])

    @property
    def duration(self) -> int:
        if not self.collection.find_one({"fingerprint": self.fingerprint}):
            raise RelayNotSubscribedError(self.data.nickname, self.fingerprint)
        notifs: Mapping[str, Any] = self.collection.find_one(
            {"fingerprint": self.fingerprint}
        )
        return notifs["NODE_DOWN"]["duration"]

    @property
    def email(self) -> str:
        if not self.collection.find_one({"fingerprint": self.fingerprint}):
            raise RelayNotSubscribedError(self.data.nickname, self.fingerprint)
        notifs: Mapping[str, Any] = self.collection.find_one(
            {"fingerprint": self.fingerprint}
        )
        return notifs["email"]

    def __validate_fingerprint(self):
        """Validate whether the relay fingerprint exists.

        Raises:
            InvalidFingerprintError: Relay fingerprint not found on onionoo API.
        """
        with requests.Session() as session:
            session.headers = CaseInsensitiveDict(  # type: ignore
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko)Chrome/94.0.4606.81 Safari/537.36"
                }
            )
            response = session.get(f"{self.url}?search={self.fingerprint}")
            if response.status_code != 200:
                raise InvalidFingerprintError(self.fingerprint)
            result = response.json()["relays"]
            if not result:
                raise InvalidFingerprintError(self.fingerprint)

    def subscribe(
        self, email: str, notifs: Sequence[Notif], duration: int = 48
    ) -> bool:
        """Subscribe to the Tor weather service.

        On subscribing, a document with relay's fingerprint, the email(s) of the
        relay provider and the type of notifications to subscribe are saved.

        Args:
            email (str): Email of relay provider.
            notifs (Sequence[Notif]): Type(s) of notification(s) to subscribe.
            duration (int): Duration before sending a notification (hours). Defaults to 48.

        Raises:
            InvalidEmailError: Email syntax/DNS server is not valid.
            RelaySubscribedError: Relay fingerprint already exists in MongoDB database.

        Returns:
            bool: True if relay data is added to database.
        """
        # Validate the email address provided by the relay provider.
        # If the email is in wrong syntax/DNS server doesn't exist
        # it raises an error.
        try:
            email_object = validate_email(email)
        except:
            raise InvalidEmailError(email)
        # If the current fingerprint exists in a document in the `torweather`
        # collection.
        if self.collection.find_one({"fingerprint": self.fingerprint}):
            raise RelaySubscribedError(self.data.nickname, self.fingerprint)
        document: MutableMapping[str, Any] = {
            "fingerprint": self.data.fingerprint,
            "email": email,
        }
        # Create a dictionary with enum variable name as key and False as value.
        # This dictionary will be used to keep track of notifications sent, thus
        # the default value is False.
        for notif in notifs:
            document[notif.name] = {"sent": False}
            if notif == Notif.NODE_DOWN:
                document[notif.name]["duration"] = duration
        self.collection.insert_one(document)
        self.logger.info(
            f"Node {self.data.nickname} (fingerprint: {self.fingerprint}) subscribed to "
            f"{', '.join([notif.name for notif in notifs])} notifications."
        )
        return True

    def unsubscribe(self) -> bool:
        """Unsubscribe from the Tor weather service.

        On unsubscribing, the document with current relay's fingerprint is
        deleted from the MongoDB database.

        Raises:
            RelayNotSubscribedError: Relay fingerprint not found in MongoDB database.

        Returns:
            bool: True if relay document is deleted from database.
        """
        # If the current fingerprint does not exist in a document in the
        # `torweather` collection.
        if not self.collection.find_one({"fingerprint": self.fingerprint}):
            raise RelayNotSubscribedError(self.data.nickname, self.fingerprint)
        self.collection.delete_one({"fingerprint": self.fingerprint})
        self.logger.info(
            f"Node {self.data.nickname} (fingerprint: {self.fingerprint}) unsubscribed."
        )
        return True

    def unsubscribe_single(self, notif_type: Notif) -> bool:
        """Unsubscribe from a single type of notification.

        Args:
            notif_type (Notif): The notification type to unsubscribe.

        Raises:
            RelayNotSubscribedError: Relay fingerprint not found in MongoDB database.
            NotifNotSubscribedError: Notification type not subscribed by relay provider.

        Returns:
            bool: True if notification is unsubscribed.
        """
        if not self.collection.find_one({"fingerprint": self.fingerprint}):
            raise RelayNotSubscribedError(self.data.nickname, self.fingerprint)
        document: Mapping[str, Any] = self.collection.find_one(
            {"fingerprint": self.fingerprint}
        )
        if notif_type.name not in document:
            raise NotifNotSubscribedError(
                self.data.nickname, self.fingerprint, notif_type
            )
        # If only a single notification is subscribed and the user
        # explicitly chooses to unsubscribe from it, delete the whole
        # relay from the database.
        if len(document) > 4:
            # The length of document should be greater than 4 as
            # every document includes _id, fingerprint, email fields.
            self.collection.update_one(
                {"fingerprint": self.fingerprint},
                {"$unset": {notif_type.name: 1}},
            )
        else:
            self.unsubscribe()
        return True

    def update_notif_status(self, notif_type: Notif, status: bool = True) -> bool:
        """Update the status of a notification subscribed by the relay operator.

        Args:
            notif_type (Notif): The notification type to update.
            status (bool, optional): Status of notification. Defaults to True.

        Raises:
            RelayNotSubscribedError: Relay fingerprint not found in MongoDB database.
            NotifNotSubscribedError: Notification type not subscribed by relay provider.

        Returns:
            bool: True if notification's status is updated in the database.
        """
        if not self.collection.find_one({"fingerprint": self.fingerprint}):
            raise RelayNotSubscribedError(self.data.nickname, self.fingerprint)
        document: Mapping[str, Any] = self.collection.find_one(
            {"fingerprint": self.fingerprint}
        )
        if notif_type.name not in document:
            raise NotifNotSubscribedError(
                self.data.nickname, self.fingerprint, notif_type
            )
        self.collection.update_one(
            {"fingerprint": self.fingerprint},
            {"$set": {f"{notif_type.name}.sent": status}},
        )
        return True
