from json import load

from telegram import Bot
from telegram.ext import CommandHandler

from TelgramWrapper.bot import TelegramBot
from deepdream.utils import Notifier


class TelegramNotifier(Notifier):

    def __init__(self, bot: Bot):
        self.bot = bot

    def notify(self, user_data: dict, message_data: dict):
        self.bot.send_message(f"link: {message_data['image']}")


IMAGE_URL_REGEX = r"http[s]??://.*\.(?:jpg|png)"


if __name__ == "__main__":
    with open("config.json", "r") as config_file:
        settings = load(config_file)
    bot = TelegramBot(settings["telegram"]["token"])
    bot.add_handler(CommandHandler())
