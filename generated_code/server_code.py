import time
from pyteal import Global, Txn
from macro.Annotations import *
from macro.Mode import Mode
from macro.Wrappers import XWrapper
test_list = [1, 2]
test_dict = {"dict": 0}


class Counter():

    def __init__(self):
        self.key = 0

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

    def match_test(self):
        match 		Global.group_size():
            case 0:
                Txn.sender()
                pass

            case 1:
                pass

    def nullify(self):
        assert algo_client.read_variable_state("counter", Mode.LOCAL) > 0
        while algo_client.read_variable_state("counter", Mode.LOCAL) > 0:
            if algo_client.read_variable_state("counter", Mode.LOCAL) == 1:
                break
            else:
                print("hey")
                continue
