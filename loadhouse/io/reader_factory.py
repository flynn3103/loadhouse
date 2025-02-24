"""Module for reader factory."""

from abc import ABC

from pyspark.sql import DataFrame

from loadhouse.core.definitions import FILE_INPUT_FORMATS, InputFormat, InputSpec
from loadhouse.io.readers.file_reader import FileReader
from loadhouse.io.readers.query_reader import QueryReader
from loadhouse.io.readers.jdbc_reader import JDBCReader
from loadhouse.io.readers.dataframe_reader import DataFrameReader

class ReaderFactory(ABC):
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
        elif spec.data_format == InputFormat.JDBC.value:
            read_df = JDBCReader(input_spec=spec).read()
        elif spec.data_format == InputFormat.SQL.value:
            read_df = QueryReader(input_spec=spec).read()
        elif spec.data_format == InputFormat.DATAFRAME.value:
            read_df = DataFrameReader(input_spec=spec).read()
        else:
            raise NotImplementedError(
                f"The requested input spec format {spec.data_format} is not supported."
            )
        return read_df