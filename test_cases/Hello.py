from macro.Annotations import *
from pyteal import *

from main import algo_client


@XAll
class Hello:

    @XOnBlockchain
    def hello(self, name: abi.String, output: abi.String):
        output.set("Hello" + " " + name.get())

    @XOnServer
    def print_hello(self, name):
        hello_text = algo_client.call_app("hello", [name])
        print(hello_text)