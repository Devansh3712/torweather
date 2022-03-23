#!/usr/bin/env python
import enum
import os
from collections.abc import Mapping
from collections.abc import Sequence
from datetime import datetime

from pydantic import BaseModel

current_directory = os.path.dirname(os.path.realpath(__file__))


class Notif(enum.Enum):
    """Enum for types of messages for TOR weather."""

    global current_directory
    with open(
        os.path.join(current_directory, "res", "messages", "node_down.txt")
    ) as content:
        NODE_DOWN: Mapping[str, str] = {
            "message": content.read(),
            "subject": "[TOR Weather] Node down",
        }
    SECURITY_VULNERABILITY: str
    END_OF_LIFE_VER: str
    OUTDATED_VER: str
    DNS_FAILURE: str
    FLAG_LOST: str
    DETECT_ISSUES: str
    SUGGESTIONS: str
    TOP_LIST: str
    DATA: str
    REQUIREMENTS: str
    OPERATOR_EVENTS: str


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
