from enum import Enum

class RegressionTestStrategy(Enum):
    AGGREGATES_RS_STAR = 1
    AGGREGATES_RS_PLUS = 2
    AGGREGATES_RS = 3
    AGGREGATES_RA = 4
    AGGREGATES_RECURSIVE = 5
    REWRITING_TIGHT = 6
    REWRITING_SHARED_CYCLE = 7
    REWRITING_LEVEL_MAPPINGS_AAAI = 8
    REWRITING_LEVEL_MAPPINGS = 9
    FULLY_GROUNDED_TIGHT = 10
    FULLY_GROUNDED_SHARED_CYCLE = 11
    FULLY_GROUNDED_LEVEL_MAPPINGS_AAAI = 12
    FULLY_GROUNDED_LEVEL_MAPPINGS = 13

