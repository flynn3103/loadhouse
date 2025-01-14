"""Module to define DataLoader class."""

from collections import OrderedDict
from copy import deepcopy
from logging import Logger
from typing import List, Optional
from lakehouse_engine.core.etl import ETL
from lakehouse_engine.utils.logging_handler import LoggingHandler
from lakehouse_engine.io.reader_factory import ReaderFactory
from lakehouse_engine.transformers.transformer_factory import TransformerFactory
from lakehouse_engine.dq_processors.validator import Validator
from lakehouse_engine.io.writer_factory import WriterFactory
from lakehouse_engine.core.definitions import (
    InputSpec,
    OutputSpec,
    OutputFormat,
    TransformerSpec,
    TransformSpec,
    DQSpec,
)


class DataLoader(ETL):
    """Load data using an ETL configuration (etl_config represented as dict)."""

    def __init__(self, etl_config: dict):
        """Construct DataLoader ETL instances.

        A data loader needs several specifications to work properly,
        but some of them might be optional. The available specifications are:

        - input specifications (mandatory): specify how to read data.
        - transform specifications (optional): specify how to transform data.
        - data quality specifications (optional): specify how to execute the data
            quality process.
        - output specifications (mandatory): specify how to write data to the
            target.
        - terminate specifications (optional): specify what to do after writing into
            the target (e.g., optimizing target table, vacuum, compute stats, etc).

        Args:
            etl_config: ETL configuration.
        """
        self._logger: Logger = LoggingHandler(self.__class__.__name__).get_logger()
        super().__init__(etl_config)
        self.input_specs: List[InputSpec] = self._get_input_specs()
        self.transform_specs: List[TransformSpec] = self._get_transform_specs()
        self.output_specs: List[OutputSpec] = self._get_output_specs()
        self.dq_specs: List[DQSpec] = self._get_dq_specs()

    def _get_input_specs(self) -> List[InputSpec]:
        """Get the input specifications from an etl_config.

        Returns:
            List of input specifications.
        """
        return [InputSpec(**spec) for spec in self.etl_config["input_specs"]]

    def _get_output_specs(self) -> List[OutputSpec]:
        """Get the output specifications from an etl_config.

        Returns:
            List of output specifications.
        """
        return [
            OutputSpec(
                spec_id=spec["spec_id"],
                input_id=spec["input_id"],
                write_type=spec.get("write_type", None),
                data_format=spec.get("data_format", OutputFormat.DELTAFILES.value),
                db_table=spec.get("db_table", None),
                location=spec.get("location", None),
                partitions=spec.get("partitions", []),
            )
            for spec in self.etl_config["output_specs"]
        ]

    def _get_transform_specs(self) -> List[TransformSpec]:
        """Get the transformation specifications from an etl_config.
        Returns:
            List of transformation specifications.
        """
        transform_specs = []
        for spec in self.etl_config.get("transform_specs", []):
            transform_spec = TransformSpec(
                spec_id=spec["spec_id"],
                input_id=spec["input_id"],
                transformers=[],
            )
            for s in spec["transformers"]:
                transformer_spec = TransformerSpec(
                    function=s["function"], args=s.get("args", {})
                )
                transform_spec.transformers.append(transformer_spec)

                transform_specs.append(transform_spec)

        return transform_specs

    def _get_dq_specs(self) -> List[DQSpec]:
        """Get list of data quality specification objects from etl_config.
        Returns:
            List of data quality spec objects.
        """
        dq_specs = []
        for spec in self.etl_config.get("dq_specs", []):
            dq_spec, dq_functions = ETL.get_dq_spec(spec)
            dq_spec.dq_functions = dq_functions
            dq_specs.append(dq_spec)
        return dq_specs

    def read(self) -> OrderedDict:
        """Read data from an input location into a distributed dataframe.

        Returns:
             An ordered dict with all the dataframes that were read.
        """
        read_dfs: OrderedDict = OrderedDict({})
        for spec in self.input_specs:
            self._logger.info(f"Found input specification: {spec}")
            read_dfs[spec.spec_id] = ReaderFactory.get_data(spec)
        return read_dfs

    def transform(self, data: OrderedDict) -> OrderedDict:
        """Transform (optionally) the data that was read.
        Args:
            data: input dataframes in an ordered dict.

        Returns:
            Another ordered dict with the transformed dataframes, according to the
            transformation specification.
        """
        if not self.transform_specs:
            return data
        else:
            transformed_dfs = OrderedDict(data)
            for spec in self.transform_specs:
                self._logger.info(f"Found transform specification: {spec}")
                transformed_df = transformed_dfs[spec.input_id]
                for transformer in spec.transformers:
                    transformed_df = transformed_df.transform(
                        TransformerFactory.get_transformer(transformer, transformed_dfs)
                    )
                transformed_dfs[spec.spec_id] = transformed_df
            return transformed_dfs

    def write(self, data: OrderedDict) -> OrderedDict:
        """Write the data that was read and transformed (if applicable).

        Args:
            data: dataframes that were read and transformed (if applicable).

        Returns:
            Dataframes that were written.
        """
        written_dfs: OrderedDict = OrderedDict({})
        for spec in self.output_specs:
            self._logger.info(f"Found output specification: {spec}")
            written_output = WriterFactory.get_writer(
                spec, data[spec.input_id], data
            ).write()
            if written_output:
                written_dfs.update(written_output)
            else:
                written_dfs[spec.spec_id] = data[spec.input_id]

        return written_dfs

    def process_dq(self, data: OrderedDict) -> OrderedDict:
        """Process the data quality tasks for the data that was read and/or transformed.
        Args:
            data: dataframes from previous steps of the ETL that we which to
                run the DQ process on.

        Returns:
            Another ordered dict with the validated dataframes.
        """
        dq_processed_dfs = OrderedDict(data)
        for spec in self.dq_specs:
            df_processed_df = dq_processed_dfs[spec.input_id]
            self._logger.info(f"Found data quality specification: {spec}")
            dq_processed_dfs[spec.spec_id] = Validator.run_dq_process(
                spec, df_processed_df
            )

    def execute(self) -> Optional[OrderedDict]:
        """Define the ETL execution behaviour."""
        try:
            self._logger.info("Starting read stage...")
            read_dfs = self.read()
            self._logger.info("Starting transform stage...")
            transformed_dfs = self.transform(read_dfs)
            self._logger.info("Starting data quality stage...")
            validated_dfs = self.process_dq(transformed_dfs)
            self._logger.info("Starting write stage...")
            written_dfs = self.write(validated_dfs)
            self._logger.info("Execution of the ETL has finished!")
        except Exception as e:
            raise e

        return written_dfs
