from enum import Enum


class TraderState(Enum):
    WAITING = 0
    BUYING = 1
    HOLDING = 2
    SELLING = 3
