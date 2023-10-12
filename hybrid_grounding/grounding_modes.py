from enum import Enum

class GroundingModes(Enum):
    RewriteAggregatesGroundPartly = 1
    RewriteAggregatesNoGround = 2
    RewriteAggregatesGroundFully = 3