#!/usr/bin/env python
"""Module for checking relay data, sending emails and upating notification status
in the background using apscheduler."""
from collections.abc import Sequence

from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient

from torweather.config import secrets
from torweather.email import Email
from torweather.relay import Relay
from torweather.schemas import Notif
from torweather.utils import node_down_duration


class Check:
    """Class for checking and updating relay notification status."""

    def __init__(self):
        """Initializes Check class with a BackgroundScheduler object."""
        self.__scheduler = BackgroundScheduler(daemon=True)
        self.scheduler.add_job(self.hourly, trigger="interval", minutes=60)
        self.scheduler.add_job(self.daily, trigger="cron", hour=0)
        self.scheduler.add_job(self.monthly, trigger="cron", day="last")

    @property
    def scheduler(self):
        """Returns the scheduler object."""
        return self.__scheduler

    def hourly(self) -> None:
        """Hourly checks of subscribed relays."""

        client = MongoClient(secrets.MONGODB_URI)
        database = client["torweather"]
        collection = database["subscribers"]
        notif_types: Sequence[str] = [
            "NODE_DOWN",
            # "SECURITY_VULNERABILITY",
            # "DNS_FAILURE",
            # "FLAG_LOST",
            # "DETECT_ISSUES",
            # "REQUIREMENTS",
        ]
        for notif in notif_types:
            cursor = collection.find({f"{notif}.sent": False})
            for data in cursor:
                relay = Relay(data["fingerprint"])
                if notif == "NODE_DOWN":
                    if node_down_duration(relay.data) > data[notif]["duration"]:
                        # getattr(Notif, notif) is used to create the enum type of Notif
                        # using the notification type stored in database.
                        Email(relay.data, data["email"], getattr(Notif, notif)).send()
                        relay.update_notif_status(getattr(Notif, notif))
                else:
                    Email(relay.data, data["email"], getattr(Notif, notif)).send()
                    relay.update_notif_status(getattr(Notif, notif))

    def daily(self) -> None:
        """Daily checks of subscribed relays."""

        client = MongoClient(secrets.MONGODB_URI)
        database = client["torweather"]
        collection = database["subscribers"]
        notif_types: Sequence[str] = [
            "OUTDATED_VER",
            # "END_OF_LIFE_VER",
            # "OPERATOR_EVENTS",
        ]
        for notif in notif_types:
            cursor = collection.find({f"{notif}.sent": False})
            for data in cursor:
                relay = Relay(data["fingerprint"])
                if notif == "OUTDATED_VER":
                    if relay.data.version_status == "unrecommended":
                        Email(relay.data, data["email"], getattr(Notif, notif)).send()
                        relay.update_notif_status(getattr(Notif, notif))
                elif notif == "END_OF_LIFE_VER":
                    if relay.data.version_status == "obsolete":
                        Email(relay.data, data["email"], getattr(Notif, notif)).send()
                        relay.update_notif_status(getattr(Notif, notif))

    def monthly(self) -> None:
        """Monthly checks of subscribed relays."""

        client = MongoClient(secrets.MONGODB_URI)
        database = client["torweather"]
        collection = database["subscribers"]
        notif_types: Sequence[str] = [
            # "TOP_LIST",
            # "DATA",
            # "SUGGESTIONS",
        ]
