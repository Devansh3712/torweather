# -*- coding: utf-8 -*-
import base64
import json
import logging
import os
from collections.abc import Mapping
from collections.abc import Sequence
from email.mime.text import MIMEText
from typing import Any
from typing import Optional

import dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from torweather.config import secrets
from torweather.exceptions import EmailSendError
from torweather.exceptions import ServiceBuildError


class Email:
    """Class for sending an email to a user using the Gmail API.

    The Gmail API has a ratelimit of 250 requests per second, and
    1 billion requests per day. An OAuth client ID is required to be
    created in order to work with the API. Once it is created, a
    `credentials.json` file is available to download which contains the
    client ID and client secret needed by Google OAuth2 for authorization.
    """

    def __init__(self) -> None:
        """Initializes the Email class with the scope used by the API
        and a custom logger."""
        self._current_directory: str = os.path.dirname(os.path.realpath(__file__))
        self._scope: Sequence[str] = ["https://mail.google.com/"]
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self._set_logging_handler()
        self._create_token_json()

    @property
    def current_directory(self) -> str:
        """Returns the path of the current directory."""
        return self._current_directory

    @property
    def scope(self) -> Sequence[str]:
        """Returns the scope used by the Gmail API."""
        return self._scope

    def _set_logging_handler(self) -> None:
        """Creates and sets a file handler for the custom logger."""
        if not os.path.isdir(os.path.join(self.current_directory, "logs")):
            os.mkdir(os.path.join(self.current_directory, "logs"))
        handler = logging.FileHandler(
            os.path.join(self.current_directory, "logs", "email.log")
        )
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(levelname)s: %(asctime)s - %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _create_token_json(self) -> None:
        """Create `token.json` from existing token data in `.env` file."""
        data: Mapping[str, Any] = {
            "token": secrets.TOKEN,
            "refresh_token": secrets.REFRESH_TOKEN,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": secrets.CLIENT_ID,
            "client_secret": secrets.CLIENT_SECRET,
            "scopes": self.scope,
            "expiry": secrets.EXPIRY,
        }
        with open(
            os.path.join(self.current_directory, "res", "token.json"), "w"
        ) as token_file:
            json.dump(data, token_file)

    def _update_env(self) -> None:
        """Update values of token environment variables in `.env` file."""
        with open(
            os.path.join(self.current_directory, "res", "token.json")
        ) as token_file:
            data = json.load(token_file)
        try:
            env_file = dotenv.find_dotenv()
            dotenv.load_dotenv(env_file)
            dotenv.set_key(env_file, "TOKEN", data["token"])
            dotenv.set_key(env_file, "REFRESH_TOKEN", data["refresh_token"])
            dotenv.set_key(env_file, "CLIENT_ID", data["client_id"])
            dotenv.set_key(env_file, "CLIENT_SECRET", data["client_secret"])
            dotenv.set_key(env_file, "EXPIRY", data["expiry"])
        except:  # For running tests using Github actions CI.
            os.environ["TOKEN"] = data["token"]
            os.environ["REFRESH_TOKEN"] = data["refresh_token"]
            os.environ["CLIENT_ID"] = data["client_id"]
            os.environ["CLIENT_SECRET"] = data["client_secret"]
            os.environ["EXPIRY"] = data["expiry"]

    def _get_message(self) -> str:
        """Returns the message to be sent."""
        with open(os.path.join(self.current_directory, "res", "message.txt")) as file:
            message: str = file.read()
            return message

    def _get_service(self) -> build:
        """Creates and returns a service object for interacting with the
        Gmail API.

        Raises:
            ServiceBuildError: Error occured while building the service object.

        Returns:
            build: Service object for interacting with the API.
        """
        token_path: str = os.path.join(self.current_directory, "res", "token.json")
        # The file `token.json` stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes
        # for the first time.
        creds = Credentials.from_authorized_user_file(token_path, self.scope)
        if not creds.valid:
            creds.refresh(Request())
            self.logger.info("API token refreshed.")
            with open(token_path, "w") as token:
                token.write(creds.to_json())
            self._update_env()
        try:
            service = build("gmail", "v1", credentials=creds)
            return service
        except:
            self.logger.error("Unable to build service object.")
            raise ServiceBuildError

    def send(self, receiver: str, subject: str) -> bool:
        """Send an email to a TOR relay provider.

        Args:
            receiver (str): Email of the receiver.
            subject (str): Subject of the email.

        Raises:
            EmailSendError: Error occured while sending the email.

        Returns:
            bool: True if email is sent succesfully.
        """
        # Multipurpose Internet Mail Extension is an internet standard,
        # encoded file format used by email programs.
        message = MIMEText(self._get_message())
        message["to"] = receiver
        message["from"] = secrets.EMAIL
        message["subject"] = subject
        # The message created using MIMEText is placed in a dictionary
        # after encoding it using base64, which is then passed in the
        # service object.
        message_base64: Mapping[str, str] = {
            "raw": base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        }
        service = self._get_service()
        try:
            result = (
                service.users()
                .messages()
                .send(userId="me", body=message_base64)
                .execute()
            )
            self.logger.info(f"Email sent to {receiver}.")
            return True
        except:
            self.logger.error(f"Unable to send email to {receiver}.")
            raise EmailSendError(receiver)
