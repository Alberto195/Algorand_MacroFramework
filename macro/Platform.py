from enum import Enum


class Platform(Enum):
    """WIP. Enum for code generation variables for locality in Smart Contract or Server.
    Args:
        BLOCKCHAIN - makes variable to be stored on Blockchain.
        DECIDE_BY_COMPILER - makes variable to be decided by compiler.
    """

    BLOCKCHAIN = 0
    DECIDE_BY_COMPILER = 1
