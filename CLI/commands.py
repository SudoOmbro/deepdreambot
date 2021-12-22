from typing import List


class Command:

    REQUIRED_ARGS = 0
    NAME = ""
    INFO = "An awesome command"

    def __init__(self, args: List[str], context: dict):
        self.args: List[str] = args
        self.context: dict = context

    def execute(self):
        if len(self.args) < self.REQUIRED_ARGS:
            print(f"{self.NAME}: Too few arguments, this command requires {self.REQUIRED_ARGS} arguments")
            return False
        return self.logic()

    def logic(self):
        """ implement command logic here, return true to close the program """
        return False

    def __str__(self):
        return f"command: '{self.NAME if self.NAME else self.__class__.__name__.lower()}'\n" \
               f"required args: {self.REQUIRED_ARGS}\n" \
               f"info: {self.INFO}\n\n"


class Exit(Command):

    INFO = "Exits the program"

    def logic(self):
        print("Ok, closing the program...")
        return True


class Test(Command):

    REQUIRED_ARGS = 2

    def logic(self):
        print(f"arg0: {self.args[0]}, arg1 {self.args[1]}")
        return False


COMMANDS = {
    "test": Test,
    "exit": Exit
}
