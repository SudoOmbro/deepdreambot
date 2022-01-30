from typing import List, Dict

from deepdream.utils import Notifier


class CliContext:

    def __init__(self):
        pass


class Command:

    REQUIRED_ARGS = 0
    NAME = ""
    INFO = "An awesome command"

    def __init__(self, args: List[str], context, commands: Dict[str, "Command.__class__"]):
        self.args: List[str] = args
        self.context = context
        self.commands = commands

    def execute(self, context: CliContext) -> bool:
        if len(self.args) < self.REQUIRED_ARGS:
            print(f"{self.NAME}: Too few arguments, this command requires {self.REQUIRED_ARGS} arguments")
            return False
        return self.logic(context)

    def logic(self, context: CliContext) -> bool:
        """ implement command logic here, return true to close the program """
        return False

    @classmethod
    def get_info(cls) -> str:
        return f"command: '{cls.NAME if cls.NAME else cls.__name__.lower()}'\n" \
               f"required args: {cls.REQUIRED_ARGS}\n" \
               f"info: {cls.INFO}\n"

    def __str__(self):
        return str(self.__dict__)


class Cli:

    def __init__(self, commands: Dict[str, Command.__class__], context):
        """
        the main CLI class, define commands and default context here

        :param commands: key-value pair dictionary (key: command string, value: command object)
        :param context: a reference to an object to be used as context, could be a dictionary or anything else
        """
        self.commands = commands
        self.context = context

    def _get_command(self) -> (Command or None) and bool:
        command_string: str = input("enter command: ")
        get_info = command_string[0] == "?"
        if get_info:
            command_string = command_string[1:]
        split_string = command_string.split(" ")
        if len(split_string) == 0:
            return None
        cmd: Command.__class__ = self.commands.get(split_string[0], None)
        if not cmd:
            print(f"Invalid command '{split_string[0]}'")
            return None, False
        if len(split_string) != 1:
            return cmd(split_string[1:], self.context, self.commands), get_info
        return cmd([], self.context, self.commands), get_info

    def run(self):
        """ call this function to run the CLI """
        while True:
            command, info = self._get_command()
            if command:
                if info:
                    print(command.get_info())
                elif command.execute(self.context):
                    return


class CliNotifier(Notifier):

    def notify(self, user_data: dict, message_data: dict):
        print(user_data, message_data)
