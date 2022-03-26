#!/usr/bin/env python
import smtplib
import ssl
from collections.abc import Sequence
from email.mime.text import MIMEText

import dotenv

import torweather.utils as utils
from torweather.config import secrets
from torweather.exceptions import EmailSendError
from torweather.logger import Logger
from torweather.relay import Relay
from torweather.schemas import Notif
from torweather.schemas import RelayData


class Email(Logger):
    """Class for sending an email to a relay provider. Secure Mail
    Transfer Protocol (SMTP) is used for sending emails.

    Attributes:
        relay_data (RelayData): Data of the relay.
        email (str): Email(s) of relay provider.
        notif_type (Message): Type of notification to be sent to the provider.
    """

    def __init__(self, relay_data: RelayData, email: str, notif_type: Notif) -> None:
        """Initializes the Email class and a logger instance."""
        super().__init__(__name__)
        self.relay = relay_data
        self.email = email
        self.type = notif_type
        self.__subject = self.type.value["subject"]
        self.__message = self.type.value["message"]

    @property
    def subject(self) -> str:
        """Returns the subject of the mail."""
        return self.__subject

    @property
    def message(self) -> str:
        """Returns the formatted content of message with relevant data of the TOR relay."""
        if self.type == Notif.NODE_DOWN:
            self.__message = self.__message.format(
                self.relay.nickname,
                self.relay.fingerprint,
                Relay(self.relay.fingerprint, testing=True).duration,
                self.relay.last_seen,
                utils.node_down_duration(self.relay),
            )
        elif self.type == Notif.OUTDATED_VER:
            self.__message = self.__message.format(
                self.relay.nickname,
                self.relay.fingerprint,
                self.relay.version_status,
            )
        return self.__message

    def send(self, server: str = "smtp.gmail.com") -> bool:
        """Send an email to a TOR relay provider using SMTP. For
        the SMTP server, either localhost or APIs like Mailgun can
        be used.

        Args:
            server (str, optional): Server domain string. Defaults to "smtp.gmail.com".

        Raises:
            EmailSendError: Error occured while sending the email.

        Returns:
            bool: True if email is sent succesfully.
        """
        # Multipurpose Internet Mail Extension is an internet standard,
        # encoded file format used by email programs.
        message = MIMEText(self.message)
        message["to"] = self.email
        message["from"] = f"Tor Weather <{secrets.EMAIL}>"
        message["subject"] = self.subject
        try:
            context = ssl.create_default_context()
            # Port 465 is used for Secure Sockets Layer (SSL).
            with smtplib.SMTP_SSL(server, 465, context=context) as smtp_server:
                smtp_server.login(secrets.EMAIL, secrets.PASSWORD)
                smtp_server.send_message(message)
            self.logger.info(f"Email sent to {self.email}.")
        except:
            self.logger.error(f"Unable to send email to {self.email}.")
            raise EmailSendError(self.email)
        return True
