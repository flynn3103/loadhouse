"""Module to read configurations."""

import importlib.resources
from typing import Any, Optional, Union

import pkg_resources
import yaml
from lakehouse_engine.utils.logging_handler import LoggingHandler
from lakehouse_engine.utils.storage.file_storage_functions import FileStorageFunctions

class ConfigUtils(object):
    """Config utilities class."""

    _LOGGER = LoggingHandler(__name__).get_logger()
    @classmethod
    def get_etl_config(
        cls,
        etl_config_path: Optional[str] = None,
        etl_config: Optional[dict] = None,
    ) -> dict:
        """Get etl_config based on a filesystem path or on a dict.

        Args:
            etl_config_path: path of the etl_config (etl config configuration) file.
            etl_config: etl_config provided directly through python code (e.g., notebooks
                or other apps).
            disable_dbfs_retry: optional flag to disable file storage dbfs.

        Returns:
            Dict representation of an etl_config.
        """
        etl_config = (
            etl_config if etl_config else ConfigUtils.read_json_etl_config(etl_config_path)
        )
        return etl_config

    @staticmethod
    def read_json_etl_config(path: str) -> Any:
        """Read an etl_config (etl config configuration) file.

        Args:
            path: path to the etl_config file.
            disable_dbfs_retry: optional flag to disable file storage dbfs.

        Returns:
            The etl_config file content as a dict.
        """
        return FileStorageFunctions.read_json(path)
    
    @staticmethod
    def get_config(package: str = "lakehouse_engine.configs") -> Any:
        """Get the lakehouse engine configuration file.

        Returns:
            Configuration dictionary
        """
        with importlib.resources.open_binary(package, "engine.yaml") as config:
            config = yaml.safe_load(config)
        return config