#!/usr/bin/env python
"""Module for handling the "/subscribe" endpoint of flask server."""
from collections.abc import Sequence

from flask import Blueprint
from flask import render_template
from flask import request

from torweather.exceptions import InvalidEmailError
from torweather.exceptions import InvalidFingerprintError
from torweather.relay import Relay
from torweather.schemas import Notif

subscribe = Blueprint("subscribe", __name__)


@subscribe.route("/", methods=["GET", "POST"], strict_slashes=False)
def main():
    """Returns rendered "subscribe.html" template according to constraints."""
    if request.method == "POST":
        email: str = request.form.get("email")
        fingerprint: str = request.form.get("fingerprint")
        node_down: str = request.form.get("node-down")
        outdated_ver: str = request.form.get("outdated-ver")
        duration: int = (
            int(request.form.get("duration"))
            if request.form.get("duration") != ""
            else 48
        )
        duration_type: str = request.form.get("duration-type")
        notifs: Sequence[Notif] = []
        if node_down == "on":
            notifs.append(Notif.NODE_DOWN)
            if duration_type == "days":
                duration *= 24
            elif duration_type == "weeks":
                duration *= 7 * 24
            elif duration_type == "months":
                duration *= 30 * 24
        if outdated_ver == "on":
            notifs.append(Notif.OUTDATED_VER)
        try:
            if not notifs:
                return render_template(
                    "subscribe.html",
                    error="Choose at least one notification to subscribe.",
                )
            relay = Relay(fingerprint)
            result: bool = relay.subscribe(email, notifs, duration)
            if result:
                return render_template(
                    "subscribe.html",
                    subscribed=True,
                    nickname=relay.data.nickname,
                    fingerprint=fingerprint,
                )
            else:
                return render_template(
                    "subscribe.html",
                    subscribed=False,
                    nickname=relay.data.nickname,
                    fingerprint=fingerprint,
                )
        except InvalidEmailError:
            return render_template("subscribe.html", error="Not a valid email address.")
        except InvalidFingerprintError:
            return render_template(
                "subscribe.html", error="Not a valid relay fingerprint."
            )
    return render_template("subscribe.html")
