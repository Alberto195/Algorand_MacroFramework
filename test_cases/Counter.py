import time

from pyteal import Global, Txn

from macro.Annotations import *
from macro.Mode import Mode
from macro.Wrappers import XWrapper

test_list = [1, 2]
test_dict = {"dict": 0}

@XAll
class Counter:

    def __init__(self):
        # blockchain var
        self.counter = XWrapper(0, Mode.LOCAL)

    @XOnBlockchain
    def increment(self):
        self.counter.set_x(self.counter.get_x() + 1)

    @XOnBlockchain
    def decrement(self):
        self.counter.set_x(self.counter.get_x() - 1)

    @XOnBlockchain
    def on_closeout(self):
        pass

    @XOnBlockchain
    def on_optin(self):
        if self.counter.get_x() == 0:
            pass
