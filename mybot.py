from json import load

from telegram import Bot
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from TelgramWrapper.bot import TelegramBot
from TelgramWrapper.generics import Chain
from TelgramWrapper.prompts import TelegramPrompt
from TelgramWrapper.variables import TelegramGetText
from deepdream.api import DeepDreamAPI
from deepdream.thread import DreamerThread
from deepdream.utils import Notifier
from keyboards import MAIN_KEYBOARD


class TelegramNotifier(Notifier):

    def __init__(self, bot: Bot):
        self.bot = bot

    def notify(self, user_data: dict, message_data: dict):
        self.bot.send_message(message_data["message"].format(message_data["link"]))


IMAGE_URL_REGEX = r"http[s]??://.*\.(?:jpg|png)"
MAIN_MENU_TEXT = "Welcome, Dreamer.\n\nWhat do you want to do?"
MAIN_MENU_PROMPT_NODEL = TelegramPrompt(MAIN_MENU_TEXT, keyboard=MAIN_KEYBOARD)
MAIN_MENU_PROMPT_DEL = TelegramPrompt(MAIN_MENU_TEXT, keyboard=MAIN_KEYBOARD, delete_last_message=True)


if __name__ == "__main__":
    # Load settings
    with open("config.json", "r") as config_file:
        settings = load(config_file)
    # initialize dreamer
    DeepDreamAPI.get_instance().set_api_key(settings["deepdream"]["apikey"])
    dreamer = DreamerThread()
    dreamer.start()
    # initialize bot
    my_bot = TelegramBot(settings["telegram"]["token"])
    # add start handler
    my_bot.add_handler(
        CommandHandler(
            "start",
            MAIN_MENU_PROMPT_DEL
        )
    )
    # add about handler
    my_bot.add_handler(
        CallbackQueryHandler(
            Chain(
                TelegramPrompt(
                    "Bot built by @LordOmbro\n\n"
                    "Code hosted [here](https://github.com/SudoOmbro/deepdreambot)\n\n"
                    "Contacts:\n"
                    "[Github](https://github.com/SudoOmbro)\n"
                    "[Instagram](https://www.instagram.com/_m_o_r_b_o_/)",
                    delete_last_message=True,
                    use_markdown=True
                ),
                MAIN_MENU_PROMPT_NODEL
            ),
            pattern="about"
        )
    )
    # add dream handler
    my_bot.add_handler(ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                TelegramPrompt(
                    "And dream you will. How many iterations shall i do? (send a number between 1 and 10)",
                    return_value=0,
                    delete_last_message=True
                ),
                pattern="dream"
            )
        ],
        states={
            0: [MessageHandler(Filters.text, Chain(
                TelegramGetText(
                    "iterations",
                    transformation_function=lambda value: int(value),
                    validation_regex=r"\b([1-9]|10)\b",
                    error_message="The given input wasn't valid"
                ),
                TelegramPrompt(
                    "{iterations} iterations it is then, now send me an image or the link of an image to dream about",
                    return_value=1
                )
            ))],
            1: []  # TODO get image and add dreamjob to dreamer
        },
        fallbacks=[CommandHandler("end", MAIN_MENU_PROMPT_DEL)]
    ))
    # start the bot and idle
    my_bot.start_and_idle()
    dreamer.kill()
