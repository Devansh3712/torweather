#!/usr/bin/env python
import os
from collections.abc import Mapping
from datetime import datetime

from torweather.schemas import RelayData


def node_down_duration(relay: RelayData) -> int:
    """Returns the duration of a TOR relay being down in hours.

    Args:
        relay (RelayData): Data of the relay to check.

    Returns:
        int: Duration of relay being down in hours.
    """
    current_time = datetime.utcnow()
    duration = current_time - relay.last_seen
    hours = divmod(duration.total_seconds(), 3600)[0]
    return int(hours)


def email_headers(subject: str, file_name: str) -> Mapping[str, str]:
    current_directory = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_directory, "messages", file_name)) as content:
        headers: Mapping[str, str] = {
            "subject": f"[Tor Weather] {subject}",
            "message": content.read(),
        }
    return headers
