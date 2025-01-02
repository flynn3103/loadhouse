"""Module to perform validations and resolve the acon."""

from lakehouse_engine.core.definitions import InputFormat, OutputFormat
from lakehouse_engine.io.exceptions import WrongIOFormatException
from lakehouse_engine.utils.logging_handler import LoggingHandler
_LOGGER = LoggingHandler(__name__).get_logger()


def validate_and_resolve_acon(acon: dict) -> dict:
    """Function to validate and resolve the acon.

    Args:
        acon: Acon to be validated and resolved.
        execution_point: Execution point to resolve the dq functions.

    Returns:
        Acon after validation and resolution.
    """
    # Performing validations
    validate_readers(acon)
    validate_writers(acon)

    _LOGGER.info(f"Read Algorithm Configuration: {str(acon)}")

    return acon


def validate_readers(acon: dict) -> None:
    """Function to validate the readers in the acon.

    Args:
        acon: Acon to be validated.

    Raises:
        RuntimeError: If the input format is not supported.
    """
    if "input_specs" in acon.keys() or "input_spec" in acon.keys():
        for spec in acon.get("input_specs", []) or [acon.get("input_spec", {})]:
            if (
                not InputFormat.exists(spec.get("data_format"))
                and "db_table" not in spec.keys()
            ):
                raise WrongIOFormatException(
                    f"Input format not supported: {spec.get('data_format')}"
                )


def validate_writers(acon: dict) -> None:
    """Function to validate the writers in the acon.

    Args:
        acon: Acon to be validated.

    Raises:
        RuntimeError: If the output format is not supported.
    """
    if "output_specs" in acon.keys() or "output_spec" in acon.keys():
        for spec in acon.get("output_specs", []) or [acon.get("output_spec", {})]:
            if not OutputFormat.exists(spec.get("data_format")):
                raise WrongIOFormatException(
                    f"Output format not supported: {spec.get('data_format')}"
                )

