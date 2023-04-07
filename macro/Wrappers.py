from macro.Mode import Mode
from macro.Platform import Platform


class XWrapper:

    def __init__(self, value, mode=Mode.GLOBAL, platform=Platform.BLOCKCHAIN):
        """A wrapper class to indicate blockchain variable.

        Args:
            value: The value passed to wrapper class, can be of any type.
            mode: Mode.GLOBAL - variable is global, Mode.LOCAL - variable is local. Defaults to global variable
            platform: Platform.BLOCKCHAIN - variable will be located on blockchain only,
                      Platform.ALL - variable will be located on both platforms.
                      Defaults to Platform.BLOCKCHAIN.
        """

        self._x = value
        self._mode = mode
        self.platform = platform

    def set_x(self, value):
        self._x = value

    def get_x(self):
        return self._x
