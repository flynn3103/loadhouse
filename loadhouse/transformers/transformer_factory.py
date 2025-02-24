"""Module with the factory pattern to return transformers."""

from typing import Callable, OrderedDict

from loadhouse.core.definitions import TransformerSpec
from loadhouse.transformers.filters import Filters

from loadhouse.utils.logging_handler import LoggingHandler


class TransformerFactory(object):
    """TransformerFactory class following the factory pattern."""

    _logger = LoggingHandler(__name__).get_logger()

    AVAILABLE_TRANSFORMERS = {
        "expression_filter": Filters.expression_filter,
    }

    @staticmethod
    def get_transformer(spec: TransformerSpec, data: OrderedDict = None) -> Callable:
        """Get a transformer following the factory pattern.

        Args:
            spec: transformer specification (individual transformation... not to be
                confused with list of all transformations).
            data: ordered dict of dataframes to be transformed. Needed when a
                transformer requires more than one dataframe as input.

        Returns:
            Transformer function to be executed in .transform() spark function.
        """
        if spec.function in TransformerFactory.AVAILABLE_TRANSFORMERS:
            return TransformerFactory.AVAILABLE_TRANSFORMERS[spec.function](**spec.args)
        else:
            raise NotImplementedError(
                f"The requested transformer {spec.function} is not implemented."
            )
