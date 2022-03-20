#!/usr/bin/env python
import pytest

from torweather import Email
from torweather import Message
from torweather import RelayData

data = {
    "nickname": "Rumtumtugger",
    "fingerprint": "000AE1F85243EEE64EBE5C14BFAA465858060C80",
    "last_seen": "2022-03-15 14:00:00",
    "running": False,
    "last_restarted": "2022-03-15 13:01:25",
    "version_status": "recommended",
    "effective_family": ["000AE1F85243EEE64EBE5C14BFAA465858060C80"],
    "email": "myemail@gmail.com",
}
relay = RelayData(**data)


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
