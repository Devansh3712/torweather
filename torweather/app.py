#!/usr/bin/env python
import os

from flask import Flask
from flask import render_template
from flask import request

from torweather.check import Check
from torweather.routes.subscribe import subscribe
from torweather.routes.unsubscribe import unsubscribe

app = Flask(__name__)
app.secret_key = os.urandom(24)
Check().scheduler.start()


@app.route("/")
@app.route("/about")
def home():
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.register_blueprint(subscribe, url_prefix="/subscribe")
    app.register_blueprint(unsubscribe, url_prefix="/unsubscribe")
    port = int(os.environ.get("PORT", 5000))
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=port)
