from datetime import datetime, timezone
import importlib
from json import dumps, loads
import json
from lakehouse_engine.core.definitions import DQSpec, OutputFormat
from lakehouse_engine.io.writer_factory import WriterFactory
from lakehouse_engine.utils.logging_handler import LoggingHandler
from pyspark.sql import DataFrame
from lakehouse_engine.core.exceptions import (
    DQCheckpointsResultsException,
    DQValidationsFailedException,
)
from pyspark.sql.functions import (
    array,
    coalesce,
    col,
    collect_list,
    concat_ws,
    dayofmonth,
    explode,
    from_json,
    lit,
    month,
    schema_of_json,
    sort_array,
    struct,
    to_json,
    to_timestamp,
    transform,
    year,
)
from pyspark.sql.types import StringType
from great_expectations.data_context.data_context.context_factory import get_context
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.data_context import EphemeralDataContext
from great_expectations.checkpoint.types.checkpoint_result import CheckpointResult
from great_expectations.data_context.types.base import (
    DataContextConfig,
    FilesystemStoreBackendDefaults,
    AnonymizedUsageStatisticsConfig,
)
from great_expectations.data_context import BaseDataContext
from lakehouse_engine.core.definitions import (
    DQDefaults,
    DQSpec,
    OutputSpec,
    WriteType,
    DQFunctionSpec,
)
from typing import Any, Dict, List, Optional, OrderedDict, Tuple, Union
from lakehouse_engine.core.exec_env import ExecEnv


class Validator(object):
    """Class containing the data quality validator."""

    _LOGGER = LoggingHandler(__name__).get_logger()
    _TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    @classmethod
    def get_dq_validator(
        cls,
        context: BaseDataContext,
        batch_request: RuntimeBatchRequest,
        expectation_suite_name: str,
        dq_functions: List[DQFunctionSpec],
    ) -> Any:
        """Get a validator according to the specification.

        Args:
            context: the BaseDataContext containing the configurations for the data
                source and store backend.
            batch_request: run time batch request to be able to query underlying data.
            expectation_suite_name: name of the expectation suite.
            dq_functions: a list of DQFunctionSpec to consider in the expectation suite.

        Returns:
            The validator with the expectation suite stored.
        """
        validator = context.get_validator(
            batch_request=batch_request, expectation_suite_name=expectation_suite_name
        )
        if dq_functions:
            for dq_function in dq_functions:
                getattr(validator, dq_function.function)(
                    **dq_function.args if dq_function.args else {}
                )

        return validator.save_expectation_suite(discard_failed_expectations=False)

    @classmethod
    def run_dq_process(cls, dq_spec: DQSpec, data: DataFrame) -> DataFrame:
        """Run the specified data quality process on a dataframe.

        Args:
            dq_spec: data quality specification.
            data: input dataframe to run the dq process on.

        Returns:
            The DataFrame containing the results of the DQ process.
        """
        context = get_context()
        context.add_datasource(**cls._get_data_source_defaults(dq_spec))
        batch_request = cls._get_batch_request(dq_spec, data)
        expectation_suite_name = (
            dq_spec.expectation_suite_name
            if dq_spec.expectation_suite_name
            else f"{dq_spec.spec_id}-{dq_spec.input_id}-{dq_spec.dq_type}"
        )
        context.add_or_update_expectation_suite(
            expectation_suite_name=expectation_suite_name
        )
        cls.get_dq_validator(
            context,
            batch_request,
            expectation_suite_name,
            dq_spec.dq_functions,
        )
        results, results_df = cls._configure_and_run_checkpoint(
            dq_spec, context, batch_request, expectation_suite_name
        )
        cls._write_to_result_sink(dq_spec, results_df)
        cls._log_or_fail(results, results_df, dq_spec)
        return data

    @classmethod
    def _log_or_fail(
        cls, results: CheckpointResult, df: DataFrame, dq_spec: DQSpec
    ) -> None:
        """Log the execution of the Data Quality process.

        Args:
            results: the results of the DQ process.
            dq_spec: data quality specification.
        """
        if results["success"]:
            cls._LOGGER.info(
                "The data passed all the expectations defined. Everything looks good!"
            )
        else:
            if dq_spec.fail_on_error:
                cls._LOGGER.info(df.show())
                raise DQValidationsFailedException("Data Quality Validations Failed!")

    @classmethod
    def _write_to_result_sink(
        cls,
        dq_spec: DQSpec,
        df: DataFrame,
        data: OrderedDict = None,
    ) -> None:
        """Write dq results dataframe to a table or location.

        Args:
            dq_spec: data quality specification.
            df: dataframe with dq results to write.
            data: list of all dfs generated on previous steps before writer.
        """
        WriterFactory.get_writer(
            spec=OutputSpec(
                spec_id="dq_result_sink",
                input_id="dq_result",
                location=dq_spec.result_sink_location,
                partitions=(
                    dq_spec.result_sink_partitions
                    if dq_spec.result_sink_partitions
                    else []
                ),
                write_type=WriteType.OVERWRITE.value,
                data_format=OutputFormat.DELTAFILES.value,
            ),
            df=df,
            data=data,
        ).write()

    @classmethod
    def _configure_and_run_checkpoint(
        cls,
        dq_spec: DQSpec,
        context: EphemeralDataContext,
        batch_request: RuntimeBatchRequest,
        expectation_suite_name: str,
    ) -> Tuple[CheckpointResult, DataFrame]:
        """Configure, run and return checkpoint results.

        A checkpoint is what enables us to run the validations of the expectations'
        suite on the batches of data.

        Args:
            dq_spec: data quality specification.
            context: the EphemeralDataContext containing the configurations for the data
                source and store backend.
            batch_request: run time batch request to be able to query underlying data.
            expectation_suite_name: name of the expectation suite.

        Returns:
            The checkpoint results in two types: CheckpointResult and Dataframe.
        """
        checkpoint_name = f"{dq_spec.spec_id}-{dq_spec.input_id}-checkpoint"
        context.add_or_update_checkpoint(
            name=checkpoint_name,
            class_name=DQDefaults.DATA_CHECKPOINTS_CLASS_NAME.value,
            config_version=DQDefaults.DATA_CHECKPOINTS_CONFIG_VERSION.value,
            run_name_template=f"%Y%m%d-%H%M%S-{checkpoint_name}",
        )

        result_format: Dict[str, Any] = {
            "result_format": dq_spec.gx_result_format,
        }

        results = context.run_checkpoint(
            checkpoint_name=checkpoint_name,
            validations=[
                {
                    "batch_request": batch_request,
                    "expectation_suite_name": expectation_suite_name,
                }
            ],
            result_format=result_format,
        )

        return results, cls._transform_checkpoint_results(
            results.to_json_dict(), dq_spec
        )

    @classmethod
    def _transform_checkpoint_results(
        cls, checkpoint_results: dict, dq_spec: DQSpec
    ) -> DataFrame:
        # TODO: Explode Transform format
        """Transforms the checkpoint results and creates new entries.

        Args:
            checkpoint_results: dict with results of the checkpoint run.
            dq_spec: data quality specification.

        Returns:
            Transformed results dataframe.
        """
        results_json_dict = loads(dumps(checkpoint_results))

        results_dict = {}
        for key, value in results_json_dict.items():
            if key == "run_results":
                checkpoint_result_identifier = list(value.keys())[0]
                # check if the grabbed identifier is correct
                if (
                    str(checkpoint_result_identifier)
                    .lower()
                    .startswith(DQDefaults.VALIDATION_COLUMN_IDENTIFIER.value)
                ):
                    results_dict["validation_result_identifier"] = (
                        checkpoint_result_identifier
                    )
                    results_dict["run_results"] = value[checkpoint_result_identifier]
                else:
                    raise DQCheckpointsResultsException(
                        "The checkpoint result identifier format is not "
                        "in accordance to what is expected"
                    )
            else:
                results_dict[key] = value

        df = ExecEnv.SESSION.createDataFrame(
            [json.dumps(results_dict)],
            schema=StringType(),
        )
        schema = schema_of_json(df.select("value").head()[0])
        df = df.withColumn("value", from_json("value", schema)).select("value.*")

        cols_to_expand = ["run_id"]
        df = (
            df.select(
                [
                    col(c) if c not in cols_to_expand else col(f"{c}.*")
                    for c in df.columns
                ]
            )
            .drop(*cols_to_expand)
            .withColumn("spec_id", lit(dq_spec.spec_id))
            .withColumn("input_id", lit(dq_spec.input_id))
        )
        results_df = cls._explode_results(df, dq_spec)

        return results_df

    @classmethod
    def _explode_results(
        cls,
        df: DataFrame,
        dq_spec: DQSpec,
    ) -> DataFrame:
        """Transform dq results dataframe exploding a set of columns.

        Args:
            df: dataframe with dq results to be exploded.
            dq_spec: data quality specification.
        """
        df = df.withColumn(
            "validation_results", explode("run_results.validation_result.results")
        ).withColumn("source", lit(dq_spec.source))

        new_columns = [
            "validation_results.expectation_config.kwargs.*",
            "run_results.validation_result.statistics.*",
            "validation_results.expectation_config.expectation_type",
            "validation_results.success as expectation_success",
            "validation_results.exception_info",
        ]

        df_exploded = df.selectExpr(*df.columns, *new_columns).drop(
            *[c.replace(".*", "").split(" as")[0] for c in new_columns]
        )

        schema = df_exploded.schema.simpleString()

        return (
            df_exploded.withColumn("run_time_year", year(to_timestamp("run_time")))
            .withColumn("run_time_month", month(to_timestamp("run_time")))
            .withColumn("run_time_day", dayofmonth(to_timestamp("run_time")))
            .withColumn("checkpoint_config", to_json(col("checkpoint_config")))
            .withColumn("run_results", to_json(col("run_results")))
            .withColumn(
                "kwargs", to_json(col("validation_results.expectation_config.kwargs"))
            )
            .withColumn("validation_results", to_json(col("validation_results")))
        )

    @classmethod
    def _get_batch_request(
        cls, dq_spec: DQSpec, data: DataFrame
    ) -> RuntimeBatchRequest:
        """Get run time batch request to be able to query underlying data.

        Args:
            dq_spec: data quality process specification.
            data: input dataframe to run the dq process on.

        Returns:
            The RuntimeBatchRequest object configuration.
        """
        return RuntimeBatchRequest(
            datasource_name=f"{dq_spec.spec_id}-{dq_spec.input_id}-datasource",
            data_connector_name=f"{dq_spec.spec_id}-{dq_spec.input_id}-data_connector",
            data_asset_name=(
                dq_spec.data_asset_name
                if dq_spec.data_asset_name
                else f"{dq_spec.spec_id}-{dq_spec.input_id}"
            ),
            batch_identifiers={
                "spec_id": dq_spec.spec_id,
                "input_id": dq_spec.input_id,
                "timestamp": cls._TIMESTAMP,
            },
            runtime_parameters={"batch_data": data},
        )

    @classmethod
    def _get_data_source_defaults(cls, dq_spec: DQSpec) -> dict:
        """Get the configuration for a datasource.

        Args:
            dq_spec: data quality specification.

        Returns:
            The python dictionary with the datasource configuration.
        """
        return {
            "name": f"{dq_spec.spec_id}-{dq_spec.input_id}-datasource",
            "class_name": DQDefaults.DATASOURCE_CLASS_NAME.value,
            "execution_engine": {
                "class_name": DQDefaults.DATASOURCE_EXECUTION_ENGINE.value,
                "persist": False,
            },
            "data_connectors": {
                f"{dq_spec.spec_id}-{dq_spec.input_id}-data_connector": {
                    "module_name": DQDefaults.DATA_CONNECTORS_MODULE_NAME.value,
                    "class_name": DQDefaults.DATA_CONNECTORS_CLASS_NAME.value,
                    "assets": {
                        (
                            dq_spec.data_asset_name
                            if dq_spec.data_asset_name
                            else f"{dq_spec.spec_id}-{dq_spec.input_id}"
                        ): {"batch_identifiers": DQDefaults.DQ_BATCH_IDENTIFIERS.value}
                    },
                }
            },
        }
