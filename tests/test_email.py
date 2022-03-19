#!/usr/bin/env python
import pytest

from torweather import Email
from torweather import EmailSendError
from torweather import Message


def test_valid_send():
    result = Email(Message.NODE_DOWN).send(
        "myemail@gmail.com", "Testing torweather app."
    )
    assert result == True


def test_invalid_send():
    with pytest.raises(EmailSendError):
        result = Email(Message.NODE_DOWN).send("myemail", "Testing torweather app.")
