"""Module to read configurations."""

import importlib.resources
from typing import Any, Optional, Union

import pkg_resources
import yaml
from lakehouse_engine.utils.logging_handler import LoggingHandler

class ConfigUtils(object):
    """Config utilities class."""

    _LOGGER = LoggingHandler(__name__).get_logger()
    @staticmethod
    def get_config(package: str = "lakehouse_engine.configs") -> Any:
        """Get the lakehouse engine configuration file.

        Returns:
            Configuration dictionary
        """
        with importlib.resources.open_binary(package, "engine.yaml") as config:
            config = yaml.safe_load(config)
        return config