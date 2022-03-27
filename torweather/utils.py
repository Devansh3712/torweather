#!/usr/bin/env python
from collections.abc import Mapping
from datetime import datetime

from torweather.schemas import RelayData


def node_down_duration(relay: RelayData) -> int:
    """Returns the duration of a Tor relay being down in hours.

    Args:
        relay (RelayData): Data of the relay to check.

    Returns:
        int: Duration of relay being down in hours.
    """
    current_time = datetime.utcnow()
    duration = current_time - relay.last_seen
    hours = divmod(duration.total_seconds(), 3600)[0]
    return int(hours)
