#!/usr/bin/env python
import enum
import os


class Message(enum.Enum):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    with open(
        os.path.join(current_directory, "res", "messages", "node_down.txt")
    ) as content:
        NODE_DOWN: str = content.read()
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
