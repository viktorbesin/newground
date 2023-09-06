
from enum import Enum

class AggregateMode(Enum):
    RS_STAR = 1
    RA = 2
    RS_PLUS = 3
    RS = 4
    RECURSIVE = 5
    