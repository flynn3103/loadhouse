"""Contract of the lakehouse engine with all the available functions to be executed."""

from typing import List, Optional, OrderedDict
from lakehouse_engine.core.exec_env import ExecEnv
from lakehouse_engine.utils.configs.config_utils import ConfigUtils
from lakehouse_engine.utils.acon_utils import validate_and_resolve_acon
from lakehouse_engine.algorithms.data_loader import DataLoader


def load_data(
    acon_path: Optional[str] = None,
    acon: Optional[dict] = None,
) -> Optional[OrderedDict]:
    """Load data using the DataLoader algorithm.

    Args:
        acon_path: path of the acon (algorithm configuration) file.
        acon: acon provided directly through python code (e.g., notebooks or other apps).
        collect_engine_usage: Lakehouse usage statistics collection strategy.
        spark_confs: optional dictionary with the spark confs to be used when collecting
            the engine usage.
    """

    acon = ConfigUtils.get_acon(acon_path, acon)
    ExecEnv.get_or_create(app_name="data_loader", config=acon.get("exec_env", None))
    acon = validate_and_resolve_acon(acon)
    return DataLoader(acon).execute()
