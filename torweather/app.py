#!/usr/bin/env python
import os
from collections.abc import Sequence

from flask import Flask
from flask import render_template
from flask import request

from torweather.check import Check
from torweather.exceptions import InvalidEmailError
from torweather.exceptions import InvalidFingerprintError
from torweather.exceptions import RelayNotSubscribedError
from torweather.relay import Relay
from torweather.schemas import Notif

app = Flask(__name__)
app.secret_key = os.urandom(24)
Check().scheduler.start()


@app.route("/")
@app.route("/about")
def home():
    return render_template("about.html")


@app.route("/subscribe", methods=["GET", "POST"])
def subscribe():
    if request.method == "POST":
        email: str = request.form.get("email")
        fingerprint: str = request.form.get("fingerprint")
        node_down: str = request.form.get("node-down")  # outputs "on" if checked
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
            duration *= 24 * 7
        elif duration_type == "months":
            duration *= 24 * 7 * 30
        try:
            relay = Relay(fingerprint, testing=True)
            result = relay.subscribe(email, notifs, duration)
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


@app.route("/unsubscribe", methods=["GET", "POST"])
def unsubscribe():
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
            else:
                return render_template(
                    "unsubscribe.html",
                    unsubscribed=False,
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


if __name__ == "__main__":
    app.run()
