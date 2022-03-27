#!/usr/bin/env python
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
    if request.method == "POST":
        fingerprint: str = request.form.get("fingerprint")
        email: str = request.form.get("email")
        notif_type: str = request.form.get("unsubscribe-notifs")
        try:
            relay = Relay(fingerprint, testing=True)
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
                notif_name: str = notif_type.replace("-", "_").upper()
                notif: Notif = getattr(Notif, notif_name)
                result: bool = relay.unsubscribe_single(notif)  # type: ignore
                if result:
                    return render_template(
                        "unsubscribe.html",
                        unsubscribed=True,
                        nickname=relay.data.nickname,
                        fingerprint=fingerprint,
                        single=True,
                        notif=notif_name,
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
