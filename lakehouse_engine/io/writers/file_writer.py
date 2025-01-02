"""Module to define behaviour to write to files."""

from typing import Callable, OrderedDict

from pyspark.sql import DataFrame

from lakehouse_engine.core.definitions import OutputSpec
from lakehouse_engine.io.writer import Writer


class FileWriter(Writer):
    """Class to write data to files."""

    def __init__(self, output_spec: OutputSpec, df: DataFrame, data: OrderedDict):
        """Construct FileWriter instances.

        Args:
            output_spec: output specification
            df: dataframe to be written.
            data: list of all dfs generated on previous steps before writer.
        """
        super().__init__(output_spec, df, data)

    def write(self) -> None:
        """Write data to files."""
        self._write_to_files_in_batch_mode(self._df, self._output_spec)
        

    @staticmethod
    def _write_to_files_in_batch_mode(df: DataFrame, output_spec: OutputSpec) -> None:
        """Write to files in batch mode.

        Args:
            df: dataframe to write.
            output_spec: output specification.
        """
        breakpoint()
        df.write.format(output_spec.data_format).partitionBy(
            output_spec.partitions
        ).options(**output_spec.options if output_spec.options else {}).mode(
            output_spec.write_type
        ).save(
            output_spec.location
        )
