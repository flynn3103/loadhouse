"""Module to define the behaviour of delta merges."""

from typing import Callable, Optional, OrderedDict

from delta.tables import DeltaMergeBuilder, DeltaTable
from pyspark.sql import DataFrame

from lakehouse_engine.core.definitions import OutputFormat, OutputSpec
from lakehouse_engine.core.exec_env import ExecEnv
from lakehouse_engine.core.exceptions import WrongIOFormatException
from lakehouse_engine.io.writer import Writer


class DeltaMergeWriter(Writer):
    """Class to merge data using delta lake."""

    def __init__(self, output_spec: OutputSpec, df: DataFrame, data: OrderedDict):
        """Construct DeltaMergeWriter instances.

        Args:
            output_spec: output specification containing merge options and
                relevant information.
            df: the dataframe containing the new data to be merged.
            data: list of all dfs generated on previous steps before writer.
        """
        super().__init__(output_spec, df, data)

    def write(self) -> None:
        """Merge new data with current data."""
        delta_table = self._get_delta_table(self._output_spec)
        DeltaMergeWriter._merge(delta_table, self._output_spec, self._df)

    @staticmethod
    def _get_delta_table(output_spec: OutputSpec) -> DeltaTable:
        """Get the delta table given an output specification w/ table name or location.

        Args:
            output_spec: output specification.

        Returns:
            DeltaTable: the delta table instance.
        """
        if output_spec.db_table:
            delta_table = DeltaTable.forName(ExecEnv.SESSION, output_spec.db_table)
        elif output_spec.data_format == OutputFormat.DELTAFILES.value:
            delta_table = DeltaTable.forPath(ExecEnv.SESSION, output_spec.location)
        else:
            raise WrongIOFormatException(
                f"{output_spec.data_format} is not compatible with Delta Merge "
                f"Writer."
            )

        return delta_table

    @staticmethod
    def _insert(
        delta_merge: DeltaMergeBuilder,
        insert_predicate: Optional[str],
        insert_column_set: Optional[dict],
    ) -> DeltaMergeBuilder:
        """Get the builder of merge data with insert predicate and column set.

        Args:
            delta_merge: builder of the merge data.
            insert_predicate: condition of the insert.
            insert_column_set: rules for setting the values of
                columns that need to be inserted.

        Returns:
            DeltaMergeBuilder: builder of the merge data with insert.
        """
        if insert_predicate:
            if insert_column_set:
                delta_merge = delta_merge.whenNotMatchedInsert(
                    condition=insert_predicate,
                    values=insert_column_set,
                )
            else:
                delta_merge = delta_merge.whenNotMatchedInsertAll(
                    condition=insert_predicate
                )
        else:
            if insert_column_set:
                delta_merge = delta_merge.whenNotMatchedInsert(values=insert_column_set)
            else:
                delta_merge = delta_merge.whenNotMatchedInsertAll()

        return delta_merge

    @staticmethod
    def _merge(delta_table: DeltaTable, output_spec: OutputSpec, df: DataFrame) -> None:
        """Perform a delta lake merge according to several merge options.

        Args:
            delta_table: delta table to which to merge data.
            output_spec: output specification containing the merge options.
            df: dataframe with the new data to be merged into the delta table.
        """
        delta_merge = delta_table.alias("current").merge(
            df.alias("new"), output_spec.merge_opts.merge_predicate
        )

        if not output_spec.merge_opts.insert_only:
            if output_spec.merge_opts.delete_predicate:
                delta_merge = delta_merge.whenMatchedDelete(
                    output_spec.merge_opts.delete_predicate
                )
            delta_merge = DeltaMergeWriter._update(
                delta_merge,
                output_spec.merge_opts.update_predicate,
                output_spec.merge_opts.update_column_set,
            )

        delta_merge = DeltaMergeWriter._insert(
            delta_merge,
            output_spec.merge_opts.insert_predicate,
            output_spec.merge_opts.insert_column_set,
        )

        delta_merge.execute()

    @staticmethod
    def _update(
        delta_merge: DeltaMergeBuilder,
        update_predicate: Optional[str],
        update_column_set: Optional[dict],
    ) -> DeltaMergeBuilder:
        """Get the builder of merge data with update predicate and column set.

        Args:
            delta_merge: builder of the merge data.
            update_predicate: condition of the update.
            update_column_set: rules for setting the values of
                columns that need to be updated.

        Returns:
            DeltaMergeBuilder: builder of the merge data with update.
        """
        if update_predicate:
            if update_column_set:
                delta_merge = delta_merge.whenMatchedUpdate(
                    condition=update_predicate,
                    set=update_column_set,
                )
            else:
                delta_merge = delta_merge.whenMatchedUpdateAll(
                    condition=update_predicate
                )
        else:
            if update_column_set:
                delta_merge = delta_merge.whenMatchedUpdate(set=update_column_set)
            else:
                delta_merge = delta_merge.whenMatchedUpdateAll()

        return delta_merge
