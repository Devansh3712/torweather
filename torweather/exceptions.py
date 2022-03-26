#!/usr/bin/env python
from torweather.schemas import Notif


class EmailSendError(Exception):
    """Raised when the service object is unable to send an email.

    Attributes:
        receiver (str): Email of the receiver.
    """

    def __init__(self, receiver: str) -> None:
        self.to = receiver

    def __str__(self) -> str:
        return f"Unable to send the email to {self.to}."


class InvalidEmailError(Exception):
    """Raised when the email provided by relay provider is not valid.

    Attributes:
        email (str): Email of the relay provider.
    """

    def __init__(self, email: str) -> None:
        self.email = email

    def __str__(self) -> str:
        return f'"{self.email}" is not a valid email.'


class InvalidFingerprintError(Exception):
    """Raised when the relay fingerprint isn't found using the onionoo
    API.

    Attributes:
        fingerprint (str): Fingerprint of the relay.
    """

    def __init__(self, fingerprint: str) -> None:
        self.fingerprint = fingerprint

    def __str__(self) -> str:
        return f'"{self.fingerprint}" is not a valid TOR fingerprint.'


class NotifNotSubscribedError(Exception):
    """Raised when the notification type is not subscribed by the relay
    provider.

    Attributes:
        nickname (str): Nickname of the relay.
        fingerprint (str): Fingerprint of the relay.
        notif_type (Notif): Notification type.
    """

    def __init__(self, nickname: str, fingerprint: str, notif_type: Notif) -> None:
        self.name = nickname
        self.fingerprint = fingerprint
        self.notif = notif_type

    def __str__(self) -> str:
        return f"Relay {self.name} (fingerprint: {self.fingerprint}) has not subscribed to {self.notif} notifications."


class RelayNotSubscribedError(Exception):
    """Raised when the relay is not found in the MongoDB database.

    Attributes:
        nickname (str): Nickname of the relay.
        fingerprint (str): Fingerprint of the relay.
    """

    def __init__(self, nickname: str, fingerprint: str) -> None:
        self.name = nickname
        self.fingerprint = fingerprint

    def __str__(self) -> str:
        return f"Relay {self.name} (fingerprint: {self.fingerprint}) has not subscribed to TOR weather service."
