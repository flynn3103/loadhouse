"""Module containing the Algorithm class."""

from typing import List, Tuple
from lakehouse_engine.core.executable import Executable



class Algorithm(Executable):
    """Class to define the behavior of every algorithm based on ACONs."""

    def __init__(self, acon: dict):
        """Construct Algorithm instances.

        Args:
            acon: algorithm configuration.
        """
        self.acon = acon
        