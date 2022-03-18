# -*- coding: utf-8 -*-
import pytest

from torweather import Email
from torweather import EmailSendError


def test_valid_send():
    result = Email().send("myemail@gmail.com", "Testing torweather app.")
    assert result == True


def test_invalid_send():
    with pytest.raises(EmailSendError):
        result = Email().send("myemail", "Testing torweather app.")
