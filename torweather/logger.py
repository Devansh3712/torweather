#!/usr/bin/env python
"""Module for initializing a custom logger for torweather modules."""
import logging
import os


class Logger:
    """Class for creating a custom logger for torweather modules.

    Attributes:
        name (str): Name of the module (__name__)
    """

    def __init__(self, name: str) -> None:
        """Initializes the Logger class for creating a logger instance."""
        self.name = name
        self.__current_directory: str = os.path.dirname(os.path.realpath(__file__))
        self.__parent_directory: str = os.path.dirname(
            os.path.realpath(self.__current_directory)
        )
        self.__logger = logging.getLogger(self.name)
        self.__logger.setLevel(logging.INFO)
        self.__set_logging_handler()

    @property
    def directory(self) -> str:
        """Returns the path of the parent directory."""
        return self.__parent_directory

    @property
    def logger(self) -> logging.Logger:
        """Returns the logger object."""
        return self.__logger

    def __set_logging_handler(self) -> None:
        """Creates and sets a file handler for the custom logger."""
        if not os.path.isdir(os.path.join(self.directory, "logs")):
            os.mkdir(os.path.join(self.directory, "logs"))
        handler = logging.FileHandler(
            os.path.join(self.directory, "logs", f"{self.name}.log")
        )
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(levelname)s: %(asctime)s - %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
