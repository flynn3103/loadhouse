"""Definitions of standard values and structures for core components."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

class CollectEngineUsage(Enum):
    """Options for collecting engine usage stats.

    - enabled, enables the collection and storage of Lakehouse Engine
    usage statistics for any environment.
    - prod_only, enables the collection and storage of Lakehouse Engine
    usage statistics for production environment only.
    - disabled, disables the collection and storage of Lakehouse Engine
    usage statistics, for all environments.
    """

    ENABLED = "enabled"
    PROD_ONLY = "prod_only"
    DISABLED = "disabled"


@dataclass
class EngineConfig(object):
    """Definitions that can come from the Engine Config file.

    - dq_bucket: S3 prod bucket used to store data quality related artifacts.
    - dq_dev_bucket: S3 dev bucket used to store data quality related artifacts.
    - notif_disallowed_email_servers: email servers not allowed to be used
        for sending notifications.
    - engine_usage_path: path where the engine prod usage stats are stored.
    - engine_dev_usage_path: path where the engine dev usage stats are stored.
    - collect_engine_usage: whether to enable the collection of lakehouse
        engine usage stats or not.
    - dq_functions_column_list: list of columns to be added to the meta argument
        of GX when using PRISMA.
    """

    dq_bucket: Optional[str] = None
    dq_dev_bucket: Optional[str] = None
    notif_disallowed_email_servers: Optional[list] = None
    engine_usage_path: Optional[str] = None
    engine_dev_usage_path: Optional[str] = None
    collect_engine_usage: str = CollectEngineUsage.ENABLED.value
    dq_functions_column_list: Optional[list] = None