#!/usr/bin/env python
from pydantic import BaseSettings


class Secrets(BaseSettings):
    """Class for parsing and validating environment variables
    from `.env` file."""

    EMAIL: str
    PASSWORD: str
    TOKEN: str
    REFRESH_TOKEN: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    EXPIRY: str
    MONGODB_URI: str

    class Config:
        env_file = ".env"


secrets = Secrets()
