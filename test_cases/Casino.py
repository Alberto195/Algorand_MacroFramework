from macro.Annotations import *
from macro.Mode import Mode
from macro.Wrappers import XWrapper
from main import algo_client


@XAll
class Casino:

    def __init__(self):
        # blockchain var
        self.rolls = XWrapper(0, Mode.LOCAL)
        #server vars
        self.username = ""

    @XOnServer
    def set_username(self, username):
        self.username = username

    @XOnServer
    def count_square_of_rolls(self):
        return self.rolls.get_x() * self.rolls.get_x()

    @XOnServer
    def roll(self):
        algo_client.call_app("roll", [])

    @XOnBlockchain
    def roll(self):
        self.rolls.set_x(self.rolls.get_x() + 1)

    @XOnBlockchain
    def on_closeout(self):
        pass

    @XOnBlockchain
    def on_optin(self):
        if self.rolls.get_x() < 10:
            pass
