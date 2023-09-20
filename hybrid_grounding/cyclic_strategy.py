from enum import Enum

class CyclicStrategy(Enum):
    ASSUME_TIGHT = 1
    LEVEL_MAPPING = 2
    SHARED_CYCLE_BODY_PREDICATES = 3
    LEVEL_MAPPING_AAAI = 4