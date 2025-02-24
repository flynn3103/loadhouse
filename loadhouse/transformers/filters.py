"""Module containing the filters transformers."""

from typing import Any, Callable, List, Optional

from pyspark.sql import DataFrame
from pyspark.sql.functions import col
from loadhouse.utils.logging_handler import LoggingHandler

class Filters(object):
    """Class containing the filters transformers."""

    _logger = LoggingHandler(__name__).get_logger()

    @staticmethod
    def expression_filter(exp: str) -> Callable:
        """Filter a dataframe based on an expression.

        Args:
            exp: filter expression.

        Returns:
            A function to be called in .transform() spark function.
        """

        def inner(df: DataFrame) -> DataFrame:
            return df.filter(exp) 

        return inner