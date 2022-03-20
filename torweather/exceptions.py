#!/usr/bin/env python
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
