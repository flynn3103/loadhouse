"""Definitions of standard values and structures for core components."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

class InputFormat(Enum):
    """Formats of etl config input."""
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
    """Formats of etl config output."""
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
    """Specification of an etl config input.
    """
    spec_id: str
    read_type: str
    data_format: Optional[str] = None
    location: Optional[str] = None
    schema: Optional[dict] = None
    options: Optional[dict] = None
    schema_path: Optional[str] = None

@dataclass
class MergeOptions(object):
    """Options for a merge operation.

    - merge_predicate: predicate to apply to the merge operation so that we can
        check if a new record corresponds to a record already included in the
        historical data.
    - insert_only: indicates if the merge should only insert data (e.g., deduplicate
        scenarios).
    - delete_predicate: predicate to apply to the delete operation.
    - update_predicate: predicate to apply to the update operation.
    - insert_predicate: predicate to apply to the insert operation.
    - update_column_set: rules to apply to the update operation which allows to
        set the value for each column to be updated.
        (e.g. {"data": "new.data", "count": "current.count + 1"} )
    - insert_column_set: rules to apply to the insert operation which allows to
        set the value for each column to be inserted.
        (e.g. {"date": "updates.date", "count": "1"} )
    """
    merge_predicate: str
    insert_only: bool = False
    delete_predicate: Optional[str] = None
    update_predicate: Optional[str] = None
    insert_predicate: Optional[str] = None
    update_column_set: Optional[dict] = None
    insert_column_set: Optional[dict] = None

@dataclass
class OutputSpec(object):
    """Specification of an etl config output.

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
    merge_opts: Optional[MergeOptions] = None


@dataclass
class TransformerSpec(object):
    """Transformer Specification, i.e., a single transformation amongst many.

    - function: name of the function (or callable function) to be executed.
    - args: (not applicable if using a callable function) dict with the arguments
        to pass to the function `<k,v>` pairs with the name of the parameter of
        the function and the respective value.
    """

    function: str
    args: dict

@dataclass
class TransformSpec(object):
    """Transformation Specification.

    - spec_id: id of the terminate specification
    - input_id: id of the corresponding input
    specification.
    - transformers: list of transformers to execute.
    """

    spec_id: str
    input_id: str
    transformers: List[TransformerSpec]


@dataclass
class DQFunctionSpec(object):
    """Defines a data quality function specification.

    - function - name of the data quality function (expectation) to execute.
    It follows the great_expectations api https://greatexpectations.io/expectations/.
    - args - args of the function (expectation). Follow the same api as above.
    """

    function: str
    args: Optional[dict] = None

@dataclass
class DQSpec(object):
    """Data quality overall specification.
    - spec_id - id of the specification.
    - input_id - id of the input specification.
    - dq_type - type of DQ process to execute (e.g. validator).
    - dq_functions - list of function specifications to execute.
    - data_asset_name - name of the data asset to consider when configuring the great
        expectations' data source.
    - expectation_suite_name - name to consider for great expectations' suite.
    - gx_result_format - great expectations result format. Default: "COMPLETE".
    - result_sink_format - format of the result table (e.g. delta, parquet, kafka...)
    - result_sink_location - file system location in which to save the results of the DQ process.
    - result_sink_partitions - the list of partitions to consider.
    - fail_on_error - whether to fail the etl config if the validations of your data in
        the DQ process failed.
    - source - name of data source, to be easier to identify in analysis. If not
        specified, it is set as default <input_id>.
    """
    spec_id: str
    input_id: str
    dq_type: str
    dq_functions: Optional[List[DQFunctionSpec]] = None
    data_asset_name: Optional[str] = None
    expectation_suite_name: Optional[str] = None
    gx_result_format: Optional[str] = "COMPLETE"
    result_sink_format: str = OutputFormat.DELTAFILES.value
    result_sink_location: Optional[str] = None
    result_sink_partitions: Optional[List[str]] = None
    fail_on_error: bool = True
    source: Optional[str] = None

class DQDefaults(Enum):
    """Defaults used on the data quality process."""
    VALIDATION_COLUMN_IDENTIFIER = "validationresultidentifier"
    DATA_CHECKPOINTS_CLASS_NAME = "SimpleCheckpoint"
    DATA_CHECKPOINTS_CONFIG_VERSION = 1.0
    DATASOURCE_EXECUTION_ENGINE = "SparkDFExecutionEngine"
    DATA_CONNECTORS_MODULE_NAME = "great_expectations.datasource.data_connector"
    DATA_CONNECTORS_CLASS_NAME = "RuntimeDatetl_confignector"
    DQ_BATCH_IDENTIFIERS = ["spec_id", "input_id", "timestamp"]
    DATASOURCE_CLASS_NAME = "Datasource"
    CUSTOM_EXPECTATION_LIST = [
        "expect_column_values_to_be_date_not_older_than",
        "expect_column_pair_a_to_be_smaller_or_equal_than_b",
        "expect_multicolumn_column_a_must_equal_b_or_c",
        "expect_queried_column_agg_value_to_be",
        "expect_column_pair_date_a_to_be_greater_than_or_equal_to_date_b",
        "expect_column_pair_a_to_be_not_equal_to_b",
    ]

class WriteType(Enum):
    """Types of write operations."""
    OVERWRITE = "overwrite"
    APPEND = "append"
    UPDATE = "update"