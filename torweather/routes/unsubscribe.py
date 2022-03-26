#!/usr/bin/env python
from flask import Blueprint
from flask import render_template
from flask import request

from torweather.exceptions import InvalidEmailError
from torweather.exceptions import InvalidFingerprintError
from torweather.exceptions import RelayNotSubscribedError
from torweather.relay import Relay

unsubscribe = Blueprint("unsubscribe", __name__)


@unsubscribe.route("/", methods=["GET", "POST"], strict_slashes=False)
def main():
    if request.method == "POST":
        fingerprint: str = request.form.get("fingerprint")
        email: str = request.form.get("email")
        try:
            relay = Relay(fingerprint, testing=True)
            if email != relay.email:
                return render_template(
                    "unsubscribe.html", error="Email not subscribed by relay."
                )
            result = relay.unsubscribe()
            if result:
                return render_template(
                    "unsubscribe.html",
                    unsubscribed=True,
                    nickname=relay.data.nickname,
                    fingerprint=fingerprint,
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
    return render_template("unsubscribe.html")
