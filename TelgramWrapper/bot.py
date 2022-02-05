import logging
from typing import Tuple

from telegram import Update
from telegram.ext import Updater, CallbackContext, Dispatcher, Handler

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TelegramEvent:

    def __init__(self, update: Update, context: CallbackContext):
        """
        A convenient wrapper of received events.

        :param update: The telegram update that caused the event
        :param context: The telegram context tied to the user that caused the event
        """
        self.update: Update = update
        self.context: CallbackContext = context
        self.chat_id: int = update.effective_chat.id  # for convenience


class TelegramFunctionBlueprint:

    def __call__(self, update: Update, context: CallbackContext) -> int or None:
        return self.logic(TelegramEvent(update, context))

    def __str__(self):
        return str(self.__dict__)

    def logic(self, event: TelegramEvent):
        pass


class FunctionChain:

    def __init__(self, *args: TelegramFunctionBlueprint, return_value: bool = False):
        """
        Used to call multiple functions from a single handle, useful to avoid creating custom functions for most
        interactions with the Bot.

        :param args:
            a tuple containing the functions that will be called,
            starting from the first and finishing with the last,
            returning the last non null value if return_value is True.
        :param return_value:
            if True returns the last returned non-None value, if False it doesn't return anything.
        """
        self.functions: Tuple = args
        self.return_value: bool = return_value

    def __call__(self, update: Update, context: CallbackContext):
        last_return_value = None
        for func in self.functions:
            ret = func(update, context)
            if ret is not None:
                last_return_value = ret
        if self.return_value:
            return last_return_value


class TelegramBot:

    # TODO add default error handler

    def __init__(self, token: str):
        self.updater: Updater = Updater(token=token, use_context=True)
        self.dispatcher: Dispatcher = self.updater.dispatcher

    def add_handler(self, handler: Handler):
        self.dispatcher.add_handler(handler)

    def start(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()

    def start_and_idle(self):
        self.updater.start_polling()
        self.updater.idle()
        self.updater.stop()
