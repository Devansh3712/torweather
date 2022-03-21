#!/usr/bin/env python
import pytest

from torweather import Email
from torweather import Message
from torweather import Relay

relay = Relay("000AE1F85243EEE64EBE5C14BFAA465858060C80", "myemail@gmail.com").data


def test_valid_send():
    global relay
    result = Email(relay, Message.NODE_DOWN).send()
    assert result == True
    assert relay.notif_sent == True


def test_invalid_send():
    global relay
    with pytest.raises(Exception):
        relay.email = "myemail"
        result = Email(relay, Message.NODE_DOWN).send()
