#!/usr/bin/env python
import pytest

from torweather import Email
from torweather import Notif
from torweather import Relay

relay = Relay("000A10D43011EA4928A35F610405F92B4433B4DC", testing=True)
notif_type = Notif.NODE_DOWN


def test_valid_send():
    global relay, notif_type
    result = Email(relay.data, ["myemail@gmail.com"], notif_type).send()
    assert result == True


def test_invalid_send():
    global relay, notif_type
    with pytest.raises(Exception):
        result = Email(relay.data, ["myemail"], notif_type).send()
