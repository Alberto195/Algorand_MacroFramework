from enum import Enum


class Mode(Enum):
    """Enum for blockchain variables for locality in Smart Contract.
    Args:
        GLOBAL - makes variable global.
        LOCAL - makes variable local.
    """

    GLOBAL = 0
    LOCAL = 1
