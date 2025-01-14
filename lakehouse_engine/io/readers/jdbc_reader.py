"""Module to define behaviour to read from JDBC sources."""

from pyspark.sql import DataFrame

from lakehouse_engine.core.definitions import InputFormat, InputSpec
from lakehouse_engine.core.exec_env import ExecEnv
from lakehouse_engine.io.reader import Reader
from lakehouse_engine.core.exceptions import WrongArgumentsException


class JDBCReader(Reader):
    """Class to read from JDBC source."""

    def __init__(self, input_spec: InputSpec):
        """Construct JDBCReader instances.

        Args:
            input_spec: input specification.
        """
        super().__init__(input_spec)

    def read(self) -> DataFrame:
        """Read data from JDBC source.

        Returns:
            A dataframe containing the data from the JDBC source.
        """
        if (
            self._input_spec.options is not None
            and self._input_spec.options.get("predicates", None) is not None
        ):
            raise WrongArgumentsException("Predicates can only be used with jdbc_args.")

        options = self._input_spec.options if self._input_spec.options else {}

        if self._input_spec.jdbc_args:
            return ExecEnv.SESSION.read.options(**options).jdbc(
                **self._input_spec.jdbc_args
            )
        else:
            return (
                ExecEnv.SESSION.read.format(InputFormat.JDBC.value)
                .options(**options)
                .load()
            )