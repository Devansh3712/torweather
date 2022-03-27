#!/usr/bin/env python
"""Module for handling the "/unsubscribe" endpoint of flask server."""
import os

from bs4 import BeautifulSoup
from flask import Blueprint
from flask import render_template
from flask import request

from torweather.exceptions import InvalidEmailError
from torweather.exceptions import InvalidFingerprintError
from torweather.exceptions import NotifNotSubscribedError
from torweather.exceptions import RelayNotSubscribedError
from torweather.relay import Relay
from torweather.schemas import Notif

unsubscribe = Blueprint("unsubscribe", __name__)


@unsubscribe.route("/", methods=["GET", "POST"], strict_slashes=False)
def main():
    """Returns rendered "unsubscribe.html" template according to constraints."""
    if request.method == "POST":
        fingerprint: str = request.form.get("fingerprint")
        email: str = request.form.get("email")
        notif_type: str = request.form.get("unsubscribe-notifs")
        try:
            relay = Relay(fingerprint)
            if email != relay.email:
                return render_template(
                    "unsubscribe.html", error="Email not subscribed by relay."
                )
            if notif_type == "all":
                result: bool = relay.unsubscribe()
                if result:
                    return render_template(
                        "unsubscribe.html",
                        unsubscribed=True,
                        nickname=relay.data.nickname,
                        fingerprint=fingerprint,
                    )
            else:
                notif: Notif = getattr(Notif, notif_type.replace("-", "_").upper())
                result: bool = relay.unsubscribe_single(notif)  # type: ignore
                if result:
                    current_directory: str = os.path.dirname(os.path.realpath(__file__))
                    parent_directory: str = os.path.dirname(current_directory)
                    with open(
                        os.path.join(parent_directory, "templates", "unsubscribe.html")
                    ) as file:
                        page_data: str = file.read()
                    # Use BeautifulSoup to get the name of the single notification
                    # that was unsubscribed.
                    soup = BeautifulSoup(page_data, features="lxml")
                    return render_template(
                        "unsubscribe.html",
                        unsubscribed=True,
                        nickname=relay.data.nickname,
                        fingerprint=fingerprint,
                        single=True,
                        notif=soup.find("option", value=notif_type).text,
                    )
        except InvalidEmailError:
            return render_template(
                "unsubscribe.html", error="Not a valid email address."
            )
        except InvalidFingerprintError:
            return render_template(
                "unsubscribe.html", error="Not a valid relay fingerprint."
            )
        except RelayNotSubscribedError:
            return render_template(
                "unsubscribe.html",
                unsubscribed=False,
                nickname=relay.data.nickname,
                fingerprint=fingerprint,
            )
        except NotifNotSubscribedError:
            return render_template(
                "unsubscribe.html", error=f"Chosen notification not subscribed."
            )
    return render_template("unsubscribe.html")
