import random
import string
from typing import Optional, OrderedDict

from pyspark.sql import DataFrame
from pyspark.sql.types import StructType

import sys
import os

# Add the parent directory of lakehouse_engine to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from lakehouse_engine.core.definitions import (
    InputFormat,
    InputSpec,
    ReadType,
)
from lakehouse_engine.core.exec_env import ExecEnv
from lakehouse_engine.io.readers.file_reader import FileReader
from lakehouse_engine.utils.logging_handler import LoggingHandler
from tests.utils.exec_env_helpers import ExecEnvHelpers

class DataframeHelpers(object):
    """Class with helper functions to interact with test dataframes."""

    _logger = LoggingHandler(__name__).get_logger()

    @staticmethod
    def read_from_file(
        location: str,
        file_format: str = InputFormat.CSV.value,
        schema: Optional[dict] = None,
        options: Optional[dict] = None,
    ) -> DataFrame:
        """Read data from a file into a dataframe.

        Args:
            location: location of the file(s).
            file_format: file(s) format.
            schema: schema of the files (only works with spark schema
                StructType for now).
            options: options (e.g., spark options) to read data.

        Returns:
            The dataframe that was read.
        """
        if options is None and file_format == InputFormat.CSV.value:
            options = {"header": True, "delimiter": ",", "inferSchema": True}
        spec = InputSpec(
            spec_id=random.choice(string.ascii_letters),  # nosec
            read_type=ReadType.BATCH.value,
            data_format=file_format,
            location=location,
            schema=schema,
            options=options,
        )
        return FileReader(input_spec=spec).read()

if __name__ == "__main__":
    """Create single execution environment session."""
    ExecEnvHelpers.prepare_exec_env('2g')
    # Example usage
    DataframeHelpers._logger.info(
        "Starting the script to read data using DataframeHelpers."
    )
    location = "test/data/test.csv"  # Replace with the actual file path
    try:
        df = DataframeHelpers.read_from_file(location)
        df.show()  # Display the DataFrame content
    except Exception as e:
        DataframeHelpers._logger.error(f"Error reading the file: {e}")
