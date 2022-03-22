#!/usr/bin/env python
import pytest

from torweather import Email
from torweather import Notif
from torweather import Relay

relay = Relay(
    "000AE1F85243EEE64EBE5C14BFAA465858060C80", ["myemail@gmail.com"], [Notif.NODE_DOWN]
)


def test_valid_send():
    global relay
    for notif_type in relay.notifs:
        result = Email(relay.data, notif_type).send()
        assert result == True


def test_invalid_send():
    global relay
    with pytest.raises(Exception):
        relay.email = ["myemail"]
        for notif_type in relay.notifs:
            result = Email(relay.data, notif_type).send()
