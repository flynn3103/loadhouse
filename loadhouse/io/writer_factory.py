"""Module for writer factory."""

from abc import ABC
from typing import OrderedDict

from pyspark.sql import DataFrame
from loadhouse.core.definitions import (
    FILE_OUTPUT_FORMATS,
    OutputFormat,
    OutputSpec
)
from loadhouse.io.writer import Writer
from loadhouse.io.writers.file_writer import FileWriter


class WriterFactory(ABC):
    """Class for writer factory."""

    AVAILABLE_WRITERS = {
        OutputFormat.FILE.value: FileWriter,
    }

    @classmethod
    def _get_writer_name(cls, spec: OutputSpec) -> str:
        """Get the writer name according to the output specification.

        Args:
            OutputSpec spec: output specification to write data.

        Returns:
            Writer: writer name that will be created to write the data.
        """
        if spec.data_format in FILE_OUTPUT_FORMATS:
            writer_name = OutputFormat.FILE.value
        else:
            writer_name = spec.data_format
        return writer_name

    @classmethod
    def get_writer(cls, spec: OutputSpec, df: DataFrame, data: OrderedDict) -> Writer:
        """Get a writer according to the output specification using a factory pattern.

        Args:
            spec: output specification to write data.
            df: dataframe to be written.
            data: list of all dfs generated on previous steps before writer.

        Returns:
            Writer: writer that will write the data.
        """
        writer_name = cls._get_writer_name(spec)
        writer = cls.AVAILABLE_WRITERS.get(writer_name)
        
        if writer:
            return writer(output_spec=spec, df=df, data=data) 
        else:
            raise NotImplementedError(
                f"The requested output spec format {spec.data_format} is not supported."
            )
