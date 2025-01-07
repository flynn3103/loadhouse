"""Module containing the definition of a data quality validator."""

from typing import Any, List

from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.data_context import BaseDatetl_configtext
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, collect_set, explode, first, lit, struct, when
from lakehouse_engine.core.exec_env import ExecEnv
from lakehouse_engine.utils.logging_handler import LoggingHandler
from lakehouse_engine.core.definitions import DQFunctionSpec

class Validator(object):
    """Class containing the data quality validator."""

    _LOGGER = LoggingHandler(__name__).get_logger()

    @classmethod
    def get_dq_validator(
        cls,
        context: BaseDatetl_configtext,
        batch_request: RuntimeBatchRequest,
        expectation_suite_name: str,
        dq_functions: List[DQFunctionSpec],
    ) -> Any:
        """Get a validator according to the specification.

        Args:
            context: the BaseDatetl_configtext containing the configurations for the data
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
