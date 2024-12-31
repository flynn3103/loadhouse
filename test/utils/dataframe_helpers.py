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
    ExecEnv.get_or_create(
        app_name="Lakehouse Engine Tests",
        enable_hive_support=False,
        config={
            "spark.master": "local[2]",
            "spark.driver.memory": '2g',
            "spark.sql.warehouse.dir": "file:///app/tests/lakehouse/spark-warehouse/",  # noqa: E501
            "spark.sql.shuffle.partitions": "2",
            "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
            "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",  # noqa: E501
            "spark.jars.packages": "io.delta:delta-spark_2.12:3.2.0,org.xerial:sqlite-jdbc:3.45.3.0,com.databricks:spark-xml_2.12:0.18.0",  # noqa: E501
            "spark.jars.excludes": "net.sourceforge.f2j:arpack_combined_all",
            "spark.sql.sources.parallelPartitionDiscovery.parallelism": "2",
            "spark.sql.legacy.charVarcharAsString": True,
        },
    )
    # Example usage
    DataframeHelpers._logger.info(
        "Starting the script to read data using DataframeHelpers."
    )
    location = "/app/test/data/test.csv"  # Replace with the actual file path
    try:
        df = DataframeHelpers.read_from_file(location)
        df.show()  # Display the DataFrame content
    except Exception as e:
        DataframeHelpers._logger.error(f"Error reading the file: {e}")
