from json import load

from telegram import Bot, Update
from telegram.ext import CommandHandler, ConversationHandler, CallbackContext

from TelgramWrapper.bot import TelegramBot
from TelgramWrapper.generics import Chain
from TelgramWrapper.handlers import TextHandler, PhotoHandler, KeyboardHandler, END_CONVERSATION
from TelgramWrapper.prompts import Prompt
from TelgramWrapper.variables import GetText, GetPhoto, clear_vars
from deepdream.api import DeepDreamAPI
from deepdream.jobs_queue import DreamJob, DreamQueue
from deepdream.thread import DreamerThread
from deepdream.utils import Notifier
from keyboards import MAIN_KEYBOARD


class TelegramNotifier(Notifier):

    def __init__(self, bot: Bot):
        self.bot = bot

    def notify(self, user_data: dict, message_data: dict):
        self.bot.send_message(
            text=message_data["message"].format(message_data["image"]),
            chat_id=int(user_data["chat_id"])
        )


MAIN_MENU_TEXT = "Welcome, Dreamer.\n\nWhat do you want to do?"
MAIN_MENU_PROMPT_NODEL = Prompt(MAIN_MENU_TEXT, keyboard=MAIN_KEYBOARD)
MAIN_MENU_PROMPT_DEL = Prompt(MAIN_MENU_TEXT, keyboard=MAIN_KEYBOARD, delete_last_message=True)
IMAGE_ADDED_PROMPT = Prompt(
                            "your image has been added to the queue, you'll be notified when the processing is done."
                        )


NOTIFIER: TelegramNotifier


def add_dreamjob(update: Update, context: CallbackContext):
    # TODO switch to PyTorch implementation
    iterations: int = context.chat_data["iterations"]
    image: bytes or str = context.chat_data["image"]
    job = DreamJob(
        image,
        NOTIFIER,
        iterations,
        {
            "username": update.effective_user.name,
            "chat_id": update.effective_chat.id
        },
        0
    )
    DreamQueue.get_instance().add_job(job)


ADD_JOB_ROUTINE = Chain(
    add_dreamjob,
    IMAGE_ADDED_PROMPT,
    clear_vars,
    MAIN_MENU_PROMPT_NODEL
)


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
    # init notifier
    NOTIFIER = TelegramNotifier(my_bot.updater.bot)
    # add start handler
    my_bot.add_handler(
        CommandHandler(
            "start",
            MAIN_MENU_PROMPT_DEL
        )
    )
    # add about handler
    my_bot.add_handler(
        KeyboardHandler(
            Chain(
                Prompt(
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
            KeyboardHandler(
                Prompt(
                    "And dream you will. How many iterations shall i do? (send a number between 1 and 10)",
                    return_value=0,
                    delete_last_message=True
                ),
                pattern="dream"
            )
        ],
        states={
            0: [TextHandler(Chain(
                GetText(
                    "iterations",
                    transformation_function=lambda value: int(value),
                    validation_regex=r"\b([1-9]|10)\b",
                    error_message="The given input wasn't valid"
                ),
                Prompt(
                    "{iterations} iterations it is then, now send me an image or the link of an image to dream about",
                    return_value=1
                )
            ))],
            1: [TextHandler(Chain(
                    GetText(
                        "image",
                        validation_regex=r"http[s]??://.*\.(?:jpg|png)",
                        error_message="The given link isn't an image",
                        return_value=END_CONVERSATION
                    ),
                    ADD_JOB_ROUTINE
                )),
                PhotoHandler(Chain(
                    GetPhoto(
                        "image",
                        return_value=END_CONVERSATION
                    ),
                    ADD_JOB_ROUTINE
            ))]
        },
        fallbacks=[CommandHandler("end", MAIN_MENU_PROMPT_DEL)]
    ))
    # start the bot and idle
    my_bot.start_and_idle()
    dreamer.kill()
