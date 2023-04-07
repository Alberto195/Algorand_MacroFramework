import time
from pyteal import Global, Txn
from macro.Annotations import *
from macro.Mode import Mode
from macro.Wrappers import XWrapper
test_list = [1, 2]
test_dict = {"dict": 0}


class Counter():

    def __init__(self):
