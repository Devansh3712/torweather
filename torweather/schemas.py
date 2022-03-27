#!/usr/bin/env python
import enum
from collections.abc import Mapping
from collections.abc import Sequence
from datetime import datetime

from pydantic import BaseModel

from torweather.utils import email_headers


class Notif(enum.Enum):
    """Enum for types of notifications for Tor weather."""

    NODE_DOWN: Mapping[str, str] = email_headers("Node down", "node_down.txt")
    SECURITY_VULNERABILITY: Mapping[str, str]
    END_OF_LIFE_VER: Mapping[str, str]
    OUTDATED_VER: Mapping[str, str] = email_headers(
        "Node out of date", "outdated_version.txt"
    )
    DNS_FAILURE: Mapping[str, str]
    FLAG_LOST: Mapping[str, str]
    DETECT_ISSUES: Mapping[str, str]
    SUGGESTIONS: Mapping[str, str]
    TOP_LIST: Mapping[str, str]
    DATA: Mapping[str, str]
    REQUIREMENTS: Mapping[str, str]
    OPERATOR_EVENTS: Mapping[str, str]


class RelayData(BaseModel):
    """Pydantic model for storing and validating relay data."""

    nickname: str
    fingerprint: str
    last_seen: datetime
    running: bool
    consensus_weight: int
    last_restarted: datetime
    bandwidth_rate: int
    effective_family: Sequence[str]
    version_status: str
    recommended_version: bool
