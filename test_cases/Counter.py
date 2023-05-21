from macro.Annotations import *
from macro.Mode import Mode
from macro.Wrappers import XWrapper
from main import algo_client

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

    @XOnServer
    def increment(self):
        algo_client.call_app("increment", [])

    @XOnServer
    def decrement(self):
        algo_client.call_app("decrement", [])

    @XOnServer
    def get_counter(self):
        return self.counter.get_x()
