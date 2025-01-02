"""Module for reader factory."""

from abc import ABC

from pyspark.sql import DataFrame

from lakehouse_engine.core.definitions import FILE_INPUT_FORMATS, InputFormat, InputSpec
from lakehouse_engine.io.readers.file_reader import FileReader


class ReaderFactory(ABC):  # noqa: B024
    """Class for reader factory."""

    @classmethod
    def get_data(cls, spec: InputSpec) -> DataFrame:
        """Get data according to the input specification following a factory pattern.

        Args:
            spec: input specification to get the data.

        Returns:
            A dataframe containing the data.
        """
        if spec.data_format in FILE_INPUT_FORMATS:
            read_df = FileReader(input_spec=spec).read()
        else:
            raise NotImplementedError(
                f"The requested input spec format {spec.data_format} is not supported."
            )
        return read_df