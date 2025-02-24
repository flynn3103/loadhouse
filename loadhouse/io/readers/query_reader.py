"""Module to define behaviour to read from a query."""

from pyspark.sql import DataFrame

from loadhouse.core.definitions import InputSpec
from loadhouse.core.exec_env import ExecEnv
from loadhouse.io.reader import Reader


class QueryReader(Reader):
    """Class to read data from a query."""

    def __init__(self, input_spec: InputSpec):
        """Construct QueryReader instances.

        Args:
            input_spec: input specification.
        """
        super().__init__(input_spec)

    def read(self) -> DataFrame:
        """Read data from a query.

        Returns:
            A dataframe containing the data from the query.
        """
        return ExecEnv.SESSION.sql(self._input_spec.query)