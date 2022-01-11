from re import match

from CLI.definitions import Command
from deepdream.jobs_queue import DreamQueue, DreamJob
from deepdream.utils import CliNotifier


class CliContext:

    def __init__(self, username):
        self.username = username


class Help(Command):

    INFO = "Shows all commands with their descriptions"

    def logic(self) -> bool:
        print()
        for command in COMMANDS:
            print(str(COMMANDS[command].get_info()))
        return False


class Exit(Command):

    INFO = "Exits the program"

    def logic(self) -> bool:
        print("Ok, closing the program...")
        return True


class Test(Command):

    REQUIRED_ARGS = 2

    def logic(self) -> bool:
        print(f"arg0: {self.args[0]}, arg1: {self.args[1]}")
        return False


class Dream(Command):

    REQUIRED_ARGS = 2
    URL_REGEX = r"(https|http)://.*\.(jpg|png|gif)"
    INFO = "Add image to the dream queue.\n" \
           "arg0: image URL or local image path\n" \
           "arg1: desired iterations"

    def logic(self) -> bool:
        if match(self.URL_REGEX, self.args[0]):
            job = DreamJob(self.args[0], CliNotifier(), int(self.args[1]), {"username": self.context.username}, 0)
            DreamQueue.get_instance().add_job(job)
            return False
        with open(self.args[0], "r") as image:
            job = DreamJob(image.read(-1), CliNotifier(), int(self.args[1]), {"username": self.context.username}, 0)
            DreamQueue.get_instance().add_job(job)
        return False


COMMANDS = {
    "help": Help,
    "test": Test,
    "dream": Dream,
    "exit": Exit
}