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
        self.key = 0

    @XOnBlockchain
    def increment(self):
        self.counter.set_x(self.counter.get_x() + 1)

    @XOnBlockchain
    def decrement(self):
        self.counter.set_x(self.counter.get_x() - 1)

    @XOnServer
    def hello(self):
        c = 2
        print("Hello world")
        for x in test_list:
            print(x)
        if 1 is test_list:
            pass
        while c > 0:
            c -= some_method()
        eight = str(8)
        eight_num = 8.0
        return 0

    @XOnBlockchain
    def on_closeout(self):
        if self.counter.get_x() < 10:
            self.counter.set_x(0)
            if self.counter.set_x(0):
                pass
        elif self.counter.get_x() == 11 and time.time() > 10000 or self.counter.get_x() == 11:
            self.counter.set_x(5)
        else:
            self.counter.set_x(2)

    @XOnBlockchain
    def on_optin(self):
        assert self.counter.get_x() > 0
        if time.time() > 10000:
            pass

    @XAll
    def match_test(self):
        match Global.group_size():
            case 0:
                Txn.sender()
                pass
            case 1:
                pass

    @XAll
    def nullify(self):
        assert self.counter.get_x() > 0
        while self.counter.get_x() > 0:
            if self.counter.get_x() == 1:
                break
            else:
                print("hey")
                continue
