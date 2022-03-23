#!/usr/bin/env python
from torweather.schemas import Notif


class ServiceBuildError(Exception):
    """Raised when a service object cannot be built."""

    def __str__(self) -> str:
        return "Unable to create Gmail API client service."


class EmailSendError(Exception):
    """Raised when the service object is unable to send an email.

    Attributes:
        receiver (str): Email of the receiver.
    """

    def __init__(self, receiver: str) -> None:
        self.to = receiver

    def __str__(self) -> str:
        return f"Unable to send the email to {self.to}."


class InvalidFingerprintError(Exception):
    """Raised when the relay fingerprint isn't found using the onionoo
    API.

    Attributes:
        fingerprint (str): Fingerprint of the relay.
    """

    def __init__(self, fingerprint: str) -> None:
        self.fingerprint = fingerprint

    def __str__(self) -> str:
        return f"{self.fingerprint} is not a valid TOR fingerprint."


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
