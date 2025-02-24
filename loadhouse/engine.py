"""Contract of the lakehouse engine with all the available functions to be executed."""

from typing import List, Optional, OrderedDict
from loadhouse.core.exec_env import ExecEnv
from loadhouse.utils.configs.config_utils import ConfigUtils
from loadhouse.utils.etl_config_utils import validate_and_resolve_etl_config
from loadhouse.src.data_loader import DataLoader

def load_data(
    etl_config_path: Optional[str] = None,
    etl_config: Optional[dict] = None,
) -> Optional[OrderedDict]:
    """Load data using the DataLoader etl config.

    Args:
        etl_config_path: path of the etl_config (etl config configuration) file.
        etl_config: etl_config provided directly through python code (e.g., notebooks or other apps).
    """

    etl_config = ConfigUtils.get_etl_config(etl_config_path, etl_config)
    ExecEnv.get_or_create(app_name="data_loader", config=etl_config.get("exec_env", None))
    etl_config = validate_and_resolve_etl_config(etl_config)
    return DataLoader(etl_config).execute()
