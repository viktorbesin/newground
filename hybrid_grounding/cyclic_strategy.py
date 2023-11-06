"""
Enum for different cyclic-strategies.
"""

from enum import Enum


class CyclicStrategy(Enum):
    """
    Enum for different cyclic-strategies.
    """

    ASSUME_TIGHT = 1
    LEVEL_MAPPING = 2
    SHARED_CYCLE_BODY_PREDICATES = 3
    LEVEL_MAPPING_AAAI = 4
