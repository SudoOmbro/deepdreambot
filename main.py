from json import load

from CLI.definitions import Cli
from deepdream.api import DeepDreamAPI
from deepdream.thread import DreamerThread
from mycommands import COMMANDS, CliContext


def main():
    with open("config.json", "r") as config_file:
        settings = load(config_file)
    DeepDreamAPI.get_instance().set_api_key(settings["deepdream"]["apikey"])
    dreamer = DreamerThread()
    dreamer.start()
    context: CliContext = CliContext(input("username: "))
    cli = Cli(COMMANDS, context)
    cli.run()


if __name__ == "__main__":
    main()
