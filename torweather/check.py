#!/usr/bin/env python
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient

from torweather.config import secrets
from torweather.email import Email
from torweather.relay import Relay
from torweather.schemas import Notif
from torweather.utils import node_down_duration


class Check:
    def __init__(self):
        self.__scheduler = BackgroundScheduler(daemon=True)
        self.scheduler.add_job(self.hourly, trigger="interval", minutes=60)
        self.scheduler.add_job(self.monthly, trigger="cron", day="last")

    @property
    def scheduler(self):
        """Returns the scheduler object."""
        return self.__scheduler

    def hourly(self) -> None:
        """Hourly checks of subscribed relays."""

        client = MongoClient(secrets.MONGODB_URI)
        database = client["testtorweather"]
        collection = database["subscribers"]
        notif_types = [
            "NODE_DOWN",
            # "SECURITY_VULNERABILITY",
            # "END_OF_LIFE_VER",
            # "OUTDATED_VER",
            # "DNS_FAILURE",
            # "FLAG_LOST",
            # "DETECT_ISSUES",
            # "SUGGESTIONS",
            # "TOP_LIST",
            # "DATA",
            # "REQUIREMENTS",
            # "OPERATOR_EVENTS",
        ]
        for notif in notif_types:
            cursor = collection.find({f"{notif}.sent": False})
            if notif == "NODE_DOWN":
                for data in cursor:
                    relay = Relay(data["fingerprint"], testing=True)
                    if node_down_duration(relay.data) > data[notif]["duration"]:
                        # getattr(Notif, notif) is used to create the enum type of Notif
                        # using the notification type stored in database.
                        Email(relay.data, data["email"], getattr(Notif, notif)).send()
                        relay.update_notif_status(getattr(Notif, notif))

    def monthly(self) -> None:
        ...
