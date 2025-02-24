"""Module to define behaviour to write to console."""

from typing import Callable, OrderedDict

from pyspark.sql import DataFrame

from loadhouse.core.definitions import OutputSpec
from loadhouse.io.writer import Writer
from loadhouse.utils.logging_handler import LoggingHandler


class ConsoleWriter(Writer):
    """Class to write data to console."""

    _logger = LoggingHandler(__name__).get_logger()

    def __init__(self, output_spec: OutputSpec, df: DataFrame, data: OrderedDict):
        """Construct ConsoleWriter instances.

        Args:
            output_spec: output specification
            df: dataframe to be written.
            data: list of all dfs generated on previous steps before writer.
        """
        super().__init__(output_spec, df, data)

    def write(self) -> None:
        """Write data to console."""
        self._output_spec.options = (
            self._output_spec.options if self._output_spec.options else {}
        )
        self._logger.info("Dataframe preview:")
        self._show_df(self._df, self._output_spec)

    @staticmethod
    def _show_df(df: DataFrame, output_spec: OutputSpec) -> None:
        """Given a dataframe it applies Spark's show function to show it.

        Args:
            df: dataframe to be shown.
            output_spec: output specification.
        """
        df.show(
            n=output_spec.options.get("limit", 20),
            truncate=output_spec.options.get("truncate", True),
            vertical=output_spec.options.get("vertical", False),
        )
