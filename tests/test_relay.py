#!/usr/bin/env python
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Tuple

import pytest

from torweather import Notif
from torweather import Relay

test_relays: Sequence[Tuple[str, Sequence[Notif], Mapping[str, str]]] = [
    (
        "000A10D43011EA4928A35F610405F92B4433B4DC",
        [Notif.NODE_DOWN],
        {"nickname": "seele", "version_status": "recommended"},
    ),
    (
        "000AE1F85243EEE64EBE5C14BFAA465858060C80",
        [Notif.NODE_DOWN],
        {"nickname": "Rumtumtugger", "version_status": "recommended"},
    ),
    (
        "0011BD2485AD45D984EC4159C88FC066E5E3300E",
        [Notif.NODE_DOWN],
        {"nickname": "CalyxInstitute14", "version_status": "recommended"},
    ),
]


@pytest.mark.parametrize("fingerprint, notifs, data", test_relays)
def test_data(fingerprint: str, notifs: Sequence[Notif], data: Mapping[str, str]):
    result = Relay(fingerprint, ["myemail@gmail.com"], notifs).data
    assert result.nickname == data["nickname"]
    assert result.version_status == data["version_status"]


@pytest.mark.parametrize("fingerprint, notifs, data", test_relays)
def test_valid_subscribe(
    fingerprint: str, notifs: Sequence[Notif], data: Mapping[str, str]
):
    result = Relay(fingerprint, ["myemail@gmail.com"], notifs, testing=True).subscribe()
    assert result == True


@pytest.mark.parametrize("fingerprint, notifs, data", test_relays)
def test_invalid_subscribe(
    fingerprint: str, notifs: Sequence[Notif], data: Mapping[str, str]
):
    result = Relay(fingerprint, ["myemail@gmail.com"], notifs, testing=True).subscribe()
    assert result == False


@pytest.mark.parametrize("fingerprint, notifs, data", test_relays)
def test_valid_unsubscribe(
    fingerprint: str, notifs: Sequence[Notif], data: Mapping[str, str]
):
    result = Relay(
        fingerprint, ["myemail@gmail.com"], notifs, testing=True
    ).unsubscribe()
    assert result == True


@pytest.mark.parametrize("fingerprint, notifs, data", test_relays)
def test_invalid_unsubscribe(
    fingerprint: str, notifs: Sequence[Notif], data: Mapping[str, str]
):
    result = Relay(
        fingerprint, ["myemail@gmail.com"], notifs, testing=True
    ).unsubscribe()
    assert result == False
