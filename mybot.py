from json import load

from telegram import Bot
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler

from TelgramWrapper.bot import TelegramBot
from TelgramWrapper.generics import Chain
from TelgramWrapper.prompts import TelegramPrompt
from TelgramWrapper.variables import TelegramGetText
from deepdream.utils import Notifier


class TelegramNotifier(Notifier):

    def __init__(self, bot: Bot):
        self.bot = bot

    def notify(self, user_data: dict, message_data: dict):
        self.bot.send_message(message_data["message"].format(message_data["link"]))


IMAGE_URL_REGEX = r"http[s]??://.*\.(?:jpg|png)"


if __name__ == "__main__":
    with open("config.json", "r") as config_file:
        settings = load(config_file)
    my_bot = TelegramBot(settings["telegram"]["token"])
    my_bot.add_handler(
        CommandHandler("start", TelegramPrompt("hello there! Send me your name and i'll say hi!"))
    )
    my_bot.add_handler(
        MessageHandler(Filters.text & (~Filters.command), Chain(
            TelegramGetText("name"),
            TelegramPrompt("hi {name}!")
        ))
    )
    # my_bot.add_handler(ConversationHandler(
    #     entry_points=[],
    #     states=[],
    #     fallbacks=[]
    # ))
    my_bot.start_and_idle()
