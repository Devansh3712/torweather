#!/usr/bin/env python
from flask import Flask
from flask import render_template
from flask import request

from torweather.relay import Relay
from torweather.schemas import Notif

app = Flask(__name__)


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
        if node_down == "on":
            relay = Relay(fingerprint, testing=True)
            result = relay.subscribe([email], [Notif.NODE_DOWN])
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


@app.route("/unsubscribe")
def unsubscribe():
    return render_template("unsubscribe.html")


if __name__ == "__main__":
    app.run()
