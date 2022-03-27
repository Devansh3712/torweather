#!/usr/bin/env python
"""Module for parsing and validating environment variables."""
from pydantic import BaseSettings


class Secrets(BaseSettings):
    """Class for parsing and validating environment variables
    from `.env` file."""

    EMAIL: str
    PASSWORD: str
    MONGODB_URI: str

    class Config:
        env_file = ".env"


secrets = Secrets()
