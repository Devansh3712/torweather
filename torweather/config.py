#!/usr/bin/env python
from pydantic import BaseSettings


class Secrets(BaseSettings):
    """Class for validating environment file variables."""

    EMAIL: str
    PASSWORD: str
    TOKEN: str
    REFRESH_TOKEN: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    EXPIRY: str

    class Config:
        env_file = ".env"


secrets = Secrets()
