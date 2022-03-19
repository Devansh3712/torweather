#!/usr/bin/env python
import pytest

from torweather import Email
from torweather import Message
from torweather import Relay

data = {
    "nickname": "Rumtumtugger",
    "fingerprint": "000AE1F85243EEE64EBE5C14BFAA465858060C80",
    "email": "myemail@gmail.com",
}
relay = Relay(**data)


def test_valid_send():
    global relay
    result = Email(relay, Message.NODE_DOWN).send()
    assert result == True


def test_invalid_send():
    global relay
    with pytest.raises(Exception):
        relay.email = "myemail"
        result = Email(relay, Message.NODE_DOWN).send()
