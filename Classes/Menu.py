
class Menu:
    __menu_callbacks = []

    def __init__(self, callback_options: list):
        self.__menu_callbacks = callback_options

    def start(self):
        for callback in self.__menu_callbacks:
            print(callback.__name__)