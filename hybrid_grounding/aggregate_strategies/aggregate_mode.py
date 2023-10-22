"""
Aggregate mode enum, for knowing which aggregate strategy to execute.
"""
from enum import Enum


class AggregateMode(Enum):
    """
    Aggregate mode enum, for knowing which aggregate strategy to execute.
    """

    RS_STAR = 1
    RA = 2
    RS_PLUS = 3
    RS = 4
    RECURSIVE = 5
