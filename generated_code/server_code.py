from macro.Annotations import *
from macro.Mode import Mode
from macro.Wrappers import XWrapper
from main import algo_client


class Casino():

    def __init__(self):
        self.username = ""

    def set_username(self, username):
        self.username = username

    def count_square_of_rolls(self):
        return algo_client.read_variable_state("rolls", Mode.LOCAL)*algo_client.read_variable_state("rolls", Mode.LOCAL)

    def roll(self):
        algo_client.call_app("roll", [])
