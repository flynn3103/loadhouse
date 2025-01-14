"""Package defining all the io custom exceptions."""


class IncrementalFilterInputNotFoundException(Exception):
    """Exception for when the input of an incremental filter is not found.
    """

    pass


class WrongIOFormatException(Exception):
    """Exception for when a user provides a wrong I/O format."""

    pass


class NotSupportedException(RuntimeError):
    """Exception for when a user provides a not supported operation."""

    pass

class DQValidationsFailedException(Exception):
    """Exception for when the data quality validations fail."""

    pass


class DQCheckpointsResultsException(Exception):
    """Exception for when the checkpoint results parsing fail."""

    pass


class DQSpecMalformedException(Exception):
    """Exception for when the DQSpec is malformed."""

    pass