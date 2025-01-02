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
    def get_acon(
        cls,
        acon_path: Optional[str] = None,
        acon: Optional[dict] = None,
    ) -> dict:
        """Get acon based on a filesystem path or on a dict.

        Args:
            acon_path: path of the acon (algorithm configuration) file.
            acon: acon provided directly through python code (e.g., notebooks
                or other apps).
            disable_dbfs_retry: optional flag to disable file storage dbfs.

        Returns:
            Dict representation of an acon.
        """
        acon = (
            acon if acon else ConfigUtils.read_json_acon(acon_path)
        )
        return acon

    @staticmethod
    def read_json_acon(path: str) -> Any:
        """Read an acon (algorithm configuration) file.

        Args:
            path: path to the acon file.
            disable_dbfs_retry: optional flag to disable file storage dbfs.

        Returns:
            The acon file content as a dict.
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