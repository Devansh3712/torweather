#!/usr/bin/env python
import os
from collections.abc import Sequence

from flask import Flask
from flask import render_template
from flask import request

from torweather.relay import Relay
from torweather.schemas import Notif

app = Flask(__name__)
app.secret_key = os.urandom(24)


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
        notifs: Sequence[Notif] = []
        if node_down == "on":
            notifs.append(Notif.NODE_DOWN)
        relay = Relay(fingerprint, testing=True)
        result = relay.subscribe([email], notifs, duration)
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
    return render_template("subscribe.html")


@app.route("/unsubscribe", methods=["GET", "POST"])
def unsubscribe():
    if request.method == "POST":
        fingerprint: str = request.form.get("fingerprint")
        relay = Relay(fingerprint, testing=True)
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
    return render_template("unsubscribe.html")


if __name__ == "__main__":
    app.run(debug=True)
