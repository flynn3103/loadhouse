"""Utilities to facilitate dataframe schema management."""

from logging import Logger
from typing import Any, List, Optional

from pyspark.sql.functions import col
from pyspark.sql.types import StructType

from loadhouse.core.definitions import InputSpec
from loadhouse.core.exec_env import ExecEnv
from loadhouse.utils.logging_handler import LoggingHandler


class SchemaUtils(object):
    """Schema utils that help retrieve and manage schemas of dataframes."""

    _logger: Logger = LoggingHandler(__name__).get_logger()
    @classmethod
    def from_input_spec(cls, input_spec: InputSpec) -> Optional[StructType]:
        """Get a spark schema from an input specification.

        This covers scenarios where the schema is provided as part of the input
        specification of the etl config. Schema can come from the table specified in the
        input specification (enforce_schema_from_table) or by the dict with the spark
        schema provided there also.

        Args:
            input_spec: input specification.

        Returns:
            spark schema struct type.
        """
        if input_spec.schema_path:
            cls._logger.info(f"Reading schema from file: {input_spec.schema_path}")
            return SchemaUtils.from_file(
                input_spec.schema_path, input_spec.disable_dbfs_retry
            )
        else:
            cls._logger.info("No schema was provided... skipping enforce schema")
            return None