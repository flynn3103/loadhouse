"""Definitions of standard values and structures for core components."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

@dataclass
class EngineConfig(object):
    """Definitions that can come from the Engine Config file.

    - dq_bucket: S3 prod bucket used to store data quality related artifacts.
    - dq_dev_bucket: S3 dev bucket used to store data quality related artifacts.
    - notif_disallowed_email_servers: email servers not allowed to be used
        for sending notifications.
    - engine_usage_path: path where the engine prod usage stats are stored.
    - engine_dev_usage_path: path where the engine dev usage stats are stored.
    """
    dq_bucket: Optional[str] = None
    dq_dev_bucket: Optional[str] = None
    notif_disallowed_email_servers: Optional[list] = None
    engine_usage_path: Optional[str] = None
    engine_dev_usage_path: Optional[str] = None
    dq_functions_column_list: Optional[list] = None

class InputFormat(Enum):
    """Formats of algorithm input."""
    JDBC = "jdbc"
    AVRO = "avro"
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    DELTAFILES = "delta"
    CLOUDFILES = "cloudfiles"
    KAFKA = "kafka"
    SQL = "sql"
    SAP_BW = "sap_bw"
    SAP_B4 = "sap_b4"
    DATAFRAME = "dataframe"
    SFTP = "sftp"

    @classmethod
    def values(cls):  # type: ignore
        """Generates a list containing all enum values.

        Return:
            A list with all enum values.
        """
        return (c.value for c in cls)

    @classmethod
    def exists(cls, input_format: str) -> bool:
        """Checks if the input format exists in the enum values.

        Args:
            input_format: format to check if exists.

        Return:
            If the input format exists in our enum.
        """
        return input_format in cls.values()


class OutputFormat(Enum):
    """Formats of algorithm output."""
    JDBC = "jdbc"
    AVRO = "avro"
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    DELTAFILES = "delta"
    KAFKA = "kafka"
    CONSOLE = "console"
    NOOP = "noop"
    DATAFRAME = "dataframe"
    REST_API = "rest_api"
    FILE = "file"  # Internal use only
    TABLE = "table"  # Internal use only

    @classmethod
    def values(cls):  # type: ignore
        """Generates a list containing all enum values.

        Return:
            A list with all enum values.
        """
        return (c.value for c in cls)
    
    @classmethod
    def exists(cls, output_format: str) -> bool:
        """Checks if the output format exists in the enum values.

        Args:
            output_format: format to check if exists.

        Return:
            If the output format exists in our enum.
        """
        return output_format in cls.values()
    
# Formats of input that are considered files.
FILE_INPUT_FORMATS = [
    InputFormat.AVRO.value,
    InputFormat.JSON.value,
    InputFormat.PARQUET.value,
    InputFormat.CSV.value,
    InputFormat.DELTAFILES.value,
    InputFormat.CLOUDFILES.value,
]
# Formats of output that are considered files.
FILE_OUTPUT_FORMATS = [
    OutputFormat.AVRO.value,
    OutputFormat.JSON.value,
    OutputFormat.PARQUET.value,
    OutputFormat.CSV.value,
    OutputFormat.DELTAFILES.value,
]
class ReadType(Enum):
    """Define the types of read operations.

    - BATCH - read the data in batch mode (e.g., Spark batch).
    - STREAMING - read the data in streaming mode (e.g., Spark streaming).
    """

    BATCH = "batch"
    STREAMING = "streaming"

@dataclass
class InputSpec(object):
    """Specification of an algorithm input.

    This is very aligned with the way the execution environment connects to the sources
    (e.g., spark sources).
    """
    spec_id: str
    read_type: str
    data_format: Optional[str] = None
    location: Optional[str] = None
    schema: Optional[dict] = None
    options: Optional[dict] = None
    schema_path: Optional[str] = None

@dataclass
class OutputSpec(object):
    """Specification of an algorithm output.

    This is very aligned with the way the execution environment connects to the output
    systems (e.g., spark outputs).

    - spec_id: id of the output specification.
    - input_id: id of the corresponding input specification.
    - write_type: type of write operation.
    - data_format: format of the output. Defaults to DELTA.
    - db_table: table name in the form of `<db>.<table>`.
    - location: uri that identifies from where to write data in the specified format.
    - partitions: list of partition input_col names.
    - merge_opts: options to apply to the merge operation.
    """
    spec_id: str
    input_id: str
    write_type: str
    data_format: str = OutputFormat.DELTAFILES.value
    db_table: Optional[str] = None
    location: Optional[str] = None
    partitions: Optional[List[str]] = None
    options: Optional[dict] = None