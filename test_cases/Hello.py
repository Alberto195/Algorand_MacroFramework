from macro.Annotations import XOnBlockchain, XAll
from pyteal import *


@XAll
class Hello:

    @XOnBlockchain
    def hello(self, name: abi.String, output: abi.String):
        output.set("Hello" + " " + name.get())

    @XOnBlockchain
    def on_closeout(self):
        pass

    @XOnBlockchain
    def on_optin(self):
        pass
