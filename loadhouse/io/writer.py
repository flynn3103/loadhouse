"""Defines abstract writer behaviour."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, OrderedDict

from pyspark.sql import DataFrame
from loadhouse.core.definitions import OutputSpec
from pyspark.sql.functions import lit
from loadhouse.utils.logging_handler import LoggingHandler


class Writer(ABC):
    """Abstract Writer class."""

    def __init__(
        self, output_spec: OutputSpec, df: DataFrame, data: OrderedDict = None
    ):
        """Construct Writer instances.

        Args:
            output_spec: output specification to write data.
            df: dataframe to write.
            data: list of all dfs generated on previous steps before writer.
        """
        self._logger = LoggingHandler(self.__class__.__name__).get_logger()
        self._output_spec = output_spec
        self._df = df
        self._data = data

    @abstractmethod
    def write(self) -> Optional[OrderedDict]:
        """Abstract write method."""
        raise NotImplementedError
