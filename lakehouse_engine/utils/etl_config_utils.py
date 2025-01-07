"""Module to perform validations and resolve the etl_config."""

from lakehouse_engine.core.definitions import InputFormat, OutputFormat
from lakehouse_engine.io.exceptions import WrongIOFormatException
from lakehouse_engine.utils.logging_handler import LoggingHandler
_LOGGER = LoggingHandler(__name__).get_logger()


def validate_and_resolve_etl_config(etl_config: dict) -> dict:
    """Function to validate and resolve the etl_config.

    Args:
        etl_config: etl_config to be validated and resolved.
        execution_point: Execution point to resolve the dq functions.

    Returns:
        etl_config after validation and resolution.
    """
    # Performing validations
    validate_readers(etl_config)
    validate_writers(etl_config)

    _LOGGER.info(f"Read Algorithm Configuration: {str(etl_config)}")

    return etl_config


def validate_readers(etl_config: dict) -> None:
    """Function to validate the readers in the etl_config.

    Args:
        etl_config: etl_config to be validated.

    Raises:
        RuntimeError: If the input format is not supported.
    """
    if "input_specs" in etl_config.keys() or "input_spec" in etl_config.keys():
        for spec in etl_config.get("input_specs", []) or [etl_config.get("input_spec", {})]:
            if (
                not InputFormat.exists(spec.get("data_format"))
                and "db_table" not in spec.keys()
            ):
                raise WrongIOFormatException(
                    f"Input format not supported: {spec.get('data_format')}"
                )


def validate_writers(etl_config: dict) -> None:
    """Function to validate the writers in the etl_config.

    Args:
        etl_config: etl_config to be validated.

    Raises:
        RuntimeError: If the output format is not supported.
    """
    if "output_specs" in etl_config.keys() or "output_spec" in etl_config.keys():
        for spec in etl_config.get("output_specs", []) or [etl_config.get("output_spec", {})]:
            if not OutputFormat.exists(spec.get("data_format")):
                raise WrongIOFormatException(
                    f"Output format not supported: {spec.get('data_format')}"
                )

