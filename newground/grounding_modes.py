"""
Enum which depicts the different grounding modes.
"""
from enum import Enum


class GroundingModes(Enum):
    """
    Enum which depicts the different grounding modes.
    """

    REWRITE_AGGREGATES_GROUND_PARTLY = 1
    REWRITE_AGGREGATES_NO_GROUND = 2
    REWRITE_AGGREGATES_GROUND_FULLY = 3
