import http

from pyteal import Txn, Gtxn, InnerTxnBuilder, Expr, TxnType, TxnField
from pyteal.ast import abi
from macro.Annotations import XOnBlockchain, XAll, XOnServer
from macro.Mode import Mode
from macro.Wrappers import XWrapper
from main import algo_client

hostName = "localhost"
serverPort = 8080


@XAll
class RockPaperScissors(http.server.SimpleHTTPRequestHandler):

    def __init__(self):
        # locals
        self.opponent = XWrapper("", Mode.LOCAL)
        self.wager = XWrapper(0, Mode.LOCAL)
        self.commitment = XWrapper("", Mode.LOCAL)
        self.reveal = XWrapper("", Mode.LOCAL)

    @XOnServer
    def do_GET(self):
        if self.path.find("isButtonPressed=true") != -1:
            print("Button clicked")
            self.call_create_challenge("Oeifo839h=", "opponent_address", 1000)

        return super().do_GET()

    @XOnServer
    def call_create_challenge(self, commitment: str, receiver: str, amt: int):
        algo_client.call_app("create_challenge", [commitment], receiver, amt)

    @XOnServer
    def call_accept_challenge(self):
        algo_client.call_app("accept_challenge", [])

    @XOnServer
    def call_reveal(self):
        algo_client.call_app("reveal", [])

    @XOnBlockchain
    def create_challenge(self, commitment: abi.String):
        self.opponent.set_x(Txn.accounts[1])
        self.wager.set_x(Gtxn[1].amount())
        self.commitment.set_x(commitment.get())
        pass

    @XOnBlockchain
    def accept_challenge(self):
        self.opponent.set_x(Txn.accounts[1])
        self.wager.set_x(Gtxn[1].amount())
        self.commitment.set_x(Txn.application_args[1])
        pass

    @XOnBlockchain
    def reveal(self):
        if self.winner_account_index(self.play_value(Txn.application_args[1]),
                                     self.play_value(self.reveal.get_x())) == 2:
            self.send_reward(0, self.wager.get_x())
            self.send_reward(1, self.wager.get_x())
        else:
            self.send_reward(self.winner_account_index(
                self.play_value(Txn.application_args[1]),
                self.play_value(self.reveal.get_x(1))),
                self.wager.get_x() * 2)
        self.reset(0)
        self.reset(1)
        pass

    @XOnBlockchain
    def send_reward(self, account_index: Expr, amount: Expr):
        InnerTxnBuilder.Begin()
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: Txn.accounts[account_index],
                TxnField.amount: amount,
            }
        )
        InnerTxnBuilder.Submit()

    @XOnBlockchain
    def winner_account_index(self, play: Expr, opponent_play: Expr):
        if play == opponent_play:
            2
        elif play == ((opponent_play + 1) % 3):
            0
        else:
            1

    @XOnBlockchain
    def play_value(self, p: Expr):
         match p:
            case "r":
                0
            case "p":
                1
            case "s":
                2

    @XOnBlockchain
    def is_valid_play(self, p: Expr):
        return p == "r" or p == "p" or p == "s"

    @XOnBlockchain
    def reset(self):
        self.opponent.set_x("")
        self.wager.set_x(0)
        self.commitment.set_x("")
        self.reveal.set_x("")
