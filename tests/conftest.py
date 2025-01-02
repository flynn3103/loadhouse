"""Module to configure the test environment."""

from typing import Any, Generator

import pytest

RESOURCES = "/app/tests/resources/"
FEATURE_RESOURCES = RESOURCES + "feature"
LAKEHOUSE = "/app/tests/lakehouse/"
LAKEHOUSE_FEATURE_IN = LAKEHOUSE + "in/feature"
LAKEHOUSE_FEATURE_CONTROL = LAKEHOUSE + "control/feature"
LAKEHOUSE_FEATURE_OUT = LAKEHOUSE + "out/feature"
LAKEHOUSE_FEATURE_LOGS = LAKEHOUSE + "logs/lakehouse-engine-logs"