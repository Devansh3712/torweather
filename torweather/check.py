#!/usr/bin/env python
from apscheduler.schedulers.blocking import BlockingScheduler
from pymongo import MongoClient

from torweather.config import secrets
from torweather.email import Email
from torweather.relay import Relay
from torweather.schemas import Notif
from torweather.utils import node_down_duration


class Check:
    def __init__(self):
        self.__scheduler = BlockingScheduler()
        self.__scheduler.add_job(self.hourly, trigger="cron", hour=12)
        self.__scheduler.add_job(self.monthly, trigger="cron", day="last")

    @property
    def scheduler(self):
        # Check().scheduler.start()
        return self.__scheduler

    def hourly(self) -> None:
        """Checks data of subscribed relays, and sends an email to the relay
        provider if appropriate conditions aren't met."""

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
            cursor = collection.find({"notifs": {notif: False}})
            for data in cursor:
                relay = Relay(data["fingerprint"])
                if node_down_duration(relay.data) > 48:
                    # getattr(Notif, notif) is used to create the enum type of Notif
                    # using the notification type stored in database.
                    Email(relay.data, data["email"], getattr(Notif, notif)).send()
                    relay.update_notif_status(getattr(Notif, notif))

    def monthly(self) -> None:
        raise NotImplementedError
