"""Module containing the ETL class."""

from typing import List, Tuple,Any, Optional
from abc import ABC, abstractmethod
from loadhouse.core.definitions import (
    DQFunctionSpec,
    DQSpec,
    OutputFormat,
)


class ETL():
    """
    Abstract class defining the behaviour of every ETL based on etl_configs."""

    def __init__(self, etl_config: dict):
        """Construct ETL instances.

        Args:
            etl_config: ETL configuration.
        """
        self.etl_config = etl_config

    @abstractmethod
    def execute(self) -> Optional[Any]:
        """Define the executable component behaviour.

        E.g., the behaviour of an etl config inheriting from this.
        """
        pass

    @classmethod
    def get_dq_spec(
        cls, spec: dict
    ) -> Tuple[DQSpec, List[DQFunctionSpec], List[DQFunctionSpec]]:
        """Get data quality specification object from etl_config.

        Args:
            spec: data quality specifications.

        Returns:
            The DQSpec and the List of DQ Functions Specs.
        """
        dq_spec = DQSpec(
            spec_id=spec["spec_id"],
            input_id=spec["input_id"],
            dq_type=spec["dq_type"],
            dq_functions=[],
            result_sink_location=spec.get(
                "result_sink_location", DQSpec.result_sink_location
            ),
            result_sink_partitions=spec.get(
                "result_sink_partitions", DQSpec.result_sink_partitions
            ),
            result_sink_format=spec.get(
                "result_sink_format", OutputFormat.CSV.value
            ),
        )
        dq_functions = cls._get_dq_functions(spec, "dq_functions")
        
        return dq_spec, dq_functions

    @staticmethod
    def _get_dq_functions(spec: dict, function_key: str) -> List[DQFunctionSpec]:
        """Get DQ Functions from a DQ Spec, based on a function_key.

        Args:
            spec: data quality specifications.
            function_key: dq function key ("dq_functions").

        Returns:
            a list of DQ Function Specs.
        """
        functions = []

        if spec.get(function_key, []):
            for f in spec.get(function_key, []):
                dq_fn_spec = DQFunctionSpec(
                    function=f["dq_function"],
                    args=f.get("args", {}),
                )
                functions.append(dq_fn_spec)

        return functions
